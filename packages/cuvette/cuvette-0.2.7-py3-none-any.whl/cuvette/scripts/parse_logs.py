import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from typing import List, Optional

from beaker import BeakerError, Experiment, Job
from deviousutils.openai import generate_gpt, openai_init

from cuvette.scripts.stream_logs import stream_experiment_logs
from cuvette.scripts.utils import gather_experiments, get_default_user

# Pre-defined failure reasons (for vLLM)
FAILURE_REASONS = """
- MAX_LEN_2048: the user-specified max length is wrong, the correct max_position_embeddings is 4096
- MAX_LEN_4096: the user-specified max length is wrong, the correct max_position_embeddings is 4096
- MAX_LEN_OTHER: the user-specified max length is wrong, the correct max_position_embeddings is something else (please specify)
- OOM: it threw an out-of-memory error, so we need more GPUs
- HF_TOKEN: We don't have access to the model on huggingface
- OTHER: Some other error (if so, briefly describe in one sentence)
"""

PROMPT = """
This is a log from a compute job

LOGS:

```
{logs}
```

FAILURE REASONS:

{failure_reasons}

INSTRUCTION:

I want to know why this job failed. Please respond with one of the following failure reasons. ONLY RESPOND WITH THAT TOKEN UNLESS IT IS "OTHER". If it's "other" breifly describe what the root failure was in a short sentence.

ADDITIONAL INSTRUCTIONS:

{additional_instructions}
"""

MAX_CHARS = 100_000


@dataclass
class JobOutput:
    name: str
    logs: str
    llm_prompt: Optional[str] = None
    llm_response: Optional[str] = None

    def to_dict(self):
        return asdict(self)


def get_failed_logs(experiment):
    # # tmp davidh: get only the sanity check experiments
    # if 'arc_challenge-mc' not in experiment.name:
    #     return None

    jobs: List[Job] = experiment.jobs

    def failed(job):
        return job.status.exit_code is not None and job.status.exit_code > 0

    # Only keep failed jobs
    if not any(failed(job) for job in jobs):
        return None

    try:
        logs = stream_experiment_logs(experiment.id, do_stream=False, return_logs=True)
    except BeakerError as e:
        print(f"Failed to stop https://beaker.org/ex/{experiment.id}: {e}")
        return None

    # Get only the error traceback
    if "Traceback" in logs:
        logs = logs[logs.find("Traceback") :]

    # Truncate
    logs = logs[-MAX_CHARS:] if len(logs) > MAX_CHARS else logs

    return logs


def parse(author, workspace, limit, instructions):
    openai_init()

    experiments: List[Experiment] = gather_experiments(
        author_list=[author], workspace_name=workspace, limit=limit
    )
    print(f"Found {len(experiments)} experiments")

    # Collect logs using multithreading
    all_outputs: List[JobOutput] = []
    with ThreadPoolExecutor() as executor:
        future_to_exp = {executor.submit(get_failed_logs, exp): exp for exp in experiments}
        for future in as_completed(future_to_exp):
            experiment = future_to_exp[future]
            name = experiment.name
            try:
                logs = future.result()
                if logs is not None:
                    all_outputs += [JobOutput(name=name, logs=logs)]
            except Exception as e:
                print(f"Error processing {name}: {e}")

    # Construct LLM prompts
    for output in all_outputs:
        prompt = PROMPT.format(
            logs=output.logs, failure_reasons=FAILURE_REASONS, additional_instructions=instructions
        )

        output.llm_prompt = prompt

    # Query LLM
    responses: List[str] = generate_gpt([out.llm_prompt for out in all_outputs])

    for response, output in zip(responses, all_outputs):
        output.llm_response = response

    # Pretty print responses
    print(
        json.dumps(
            [{"name": out.name, "reason": out.llm_response} for out in all_outputs], indent=4
        )
    )


def main():
    parser = argparse.ArgumentParser(description="Analyze logs wtih ChatGPT.")
    parser.add_argument("-w", "--workspace", type=str, required=True, help="Beaker workspace name")
    parser.add_argument(
        "--author",
        "-a",
        type=str,
        default=get_default_user(),
        help="Author name to filter experiments by.",
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=100, help="Maximum number of experiments to check"
    )
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        default="",
        help="Additional instructions to the prompt when parsing the errors in the logs",
    )
    args = parser.parse_args()

    parse(args.author, args.workspace, args.limit, args.prompt)
