from typing import List

from beaker import Beaker, Experiment, Job, JobPatch

from cuvette.scripts.utils import gather_experiments, get_default_user


def change_priority(author, workspace, priority, limit=5000):
    beaker = Beaker.from_env()
    experiments: List[Experiment] = gather_experiments(
        [author],
        workspace_name=workspace,
        limit=limit,
    )
    print(f"Found {len(experiments)} failed experiments")

    for i, experiment in enumerate(experiments):
        for job in experiment.jobs:
            job: Job
            try:
                # Make direct API call to update job priority
                response = beaker.job.request(
                    f"jobs/{job.id}", method="PATCH", data=JobPatch(priority=priority)
                )
                if response.status_code == 200:
                    print(f"Updated job {job.id} priority to {priority}")
                else:
                    raise RuntimeError(f"{response.status_code} - {response.text}")
            except Exception as e:
                print(f"Failed to update priority for job {job.id}: {e}")

        print(f"({i+1}/{len(experiments)}) updated https://beaker.org/ex/{experiment.id})")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--author",
        "-a",
        type=str,
        default=get_default_user(),
        help="Author name to filter experiments by.",
    )
    parser.add_argument("-w", "--workspace", type=str, required=True, help="Beaker workspace name")
    parser.add_argument(
        "-p",
        "--priority",
        type=str,
        required=True,
        choices=["low", "normal", "high", "urgent"],
        help="Priority level to set for jobs",
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=100, help="Maximum number of experiments to check"
    )
    args = parser.parse_args()

    change_priority(args.author, args.workspace, args.priority, args.limit)


if __name__ == "__main__":
    main()
