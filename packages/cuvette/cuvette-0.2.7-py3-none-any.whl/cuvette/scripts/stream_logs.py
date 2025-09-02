import argparse
import sys

from beaker import Beaker, Job
from beaker.exceptions import JobNotFound


def stream_experiment_logs(job_id: str, do_stream: bool, return_logs: bool = False):
    beaker = Beaker.from_env()

    try:
        job: Job = beaker.job.get(job_id)

        if job.execution is None:
            if job.kind == "session":
                raise ValueError("Job is a session. Please provide an execution job.")
            raise RuntimeError(job)

        experiment_id = job.execution.experiment
    except JobNotFound:
        print(f"Job {job_id} not found, using {job_id} as an experiment ID...")
        experiment_id = job_id

    # Check if there's multiple tasks
    experiment = beaker.experiment.get(experiment_id)
    task_ids = [job.execution.task for job in experiment.jobs]
    if len(task_ids) > 1:
        task_id = [
            job.execution.task
            for job in experiment.jobs
            if job.execution.replica_rank == 0 or job.execution.replica_rank is None
        ][-1]
        print(f'Multiple tasks found! Following replica=0: "{task_id}"...')
    else:
        task_id = task_ids[0]

    try:
        if do_stream:
            for line in beaker.experiment.follow(
                experiment=experiment_id,
                task=task_id,
                strict=True,
                # since=timedelta(minutes=2)
            ):
                log_line = line.decode("utf-8", errors="replace").rstrip()
                print(log_line)
                sys.stdout.flush()
        else:
            log_stream = beaker.experiment.logs(experiment_id, quiet=True)

            logs = ""
            for line in log_stream:
                logs += line.decode("utf-8", errors="replace").rstrip()
                logs += "\n"

            if return_logs:
                return logs

            print(logs)
            sys.stdout.flush()

    except KeyboardInterrupt:
        print("\nLog streaming interrupted by user")
    except Exception as e:
        print(f"Error streaming logs: {e}")


def main():
    parser = argparse.ArgumentParser(description="Stream logs from a Beaker job")
    parser.add_argument("-j", "--job_id", help="The ID or name of the Beaker job", required=True)
    parser.add_argument(
        "-s",
        "--stream",
        help="The ID or name of the Beaker job",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    stream_experiment_logs(args.job_id, do_stream=args.stream)


def logs():
    parser = argparse.ArgumentParser(description="Get logs from a Beaker job")
    parser.add_argument("job_id", help="The ID or name of the Beaker job")

    args = parser.parse_args()

    stream_experiment_logs(args.job_id, do_stream=False)


def stream():
    parser = argparse.ArgumentParser(description="Stream logs from a Beaker job")
    parser.add_argument("job_id", help="The ID or name of the Beaker job")

    args = parser.parse_args()

    stream_experiment_logs(args.job_id, do_stream=True)
