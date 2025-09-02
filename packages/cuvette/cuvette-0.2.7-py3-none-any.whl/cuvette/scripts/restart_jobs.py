import time
from typing import List

from beaker import Beaker, Experiment
from beaker.exceptions import BeakerError

from cuvette.scripts.utils import gather_experiments, get_default_user


def beaker_experiment_failed(exp):
    """Returns if beaker experiment failed."""
    if exp.jobs[0].execution.spec.replicas is not None:
        num_replicas = exp.jobs[0].execution.spec.replicas
    else:
        num_replicas = 1

    checks = []
    for job in exp.jobs:
        if job.status.exited is None:
            return False  # at least one job is still running
        checks.append(job.status.finalized is not None and job.status.exit_code == 0)

    return sum(checks) != num_replicas


def restart_jobs(author, workspace, limit=5000):
    beaker = Beaker.from_env()
    experiments: List[Experiment] = gather_experiments(
        [author],
        workspace_name=workspace,
        limit=limit,
    )
    experiments = [exp for exp in experiments if beaker_experiment_failed(exp)]
    print(f"Found {len(experiments)} failed experiments")

    for i, experiment in enumerate(experiments):
        try:
            beaker.experiment.resume(experiment)
        except BeakerError as e:
            print(f"Failed to restart https://beaker.org/ex/{experiment.id}: {e}")
            continue

        print(f"({i+1}/{len(experiments)}) Restarted https://beaker.org/ex/{experiment.id})")

        if (i + 1) % 200 == 0:
            print("Giving the Beaker API a 20s breather to prevent overloding and timeouts...")
            time.sleep(20)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--workspace", type=str, required=True, help="Beaker workspace name")
    parser.add_argument(
        "--author",
        "-a",
        type=str,
        default=get_default_user(),
        help="Author name to filter experiments by.",
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=5000, help="Maximum number of experiments to check"
    )
    args = parser.parse_args()

    restart_jobs(args.author, args.workspace, args.limit)
