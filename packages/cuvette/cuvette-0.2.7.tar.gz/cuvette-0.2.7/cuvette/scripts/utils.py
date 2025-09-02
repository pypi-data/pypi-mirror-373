import subprocess
from typing import List

from beaker import Beaker, Experiment


def run_command(cmd, shell=True):
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def get_default_user():
    beaker: Beaker = Beaker.from_env()
    user = beaker.account.name
    return user


def gather_experiments(author_list, workspace_name, limit=2000) -> List[Experiment]:
    """Gather all failed jobs"""
    beaker = Beaker.from_env()
    experiments = []

    # Nice bookkeeping to see how many failed per author - a good gut check, if nothing else
    num_author_exps = {}
    for author in author_list:
        num_author_exps[author] = 0

    print(f'Pulling experiments from "{workspace_name}" for author(s) {author_list}...')
    exps = beaker.workspace.experiments(workspace=workspace_name, limit=limit)

    for exp in exps:
        author = exp.author.name

        # filter by author
        if author not in author_list:
            continue

        experiments.append(exp)
        num_author_exps[author] += 1

    print(f"Total experiments that failed for authors {author_list}: {len(experiments)}")
    for author, count in num_author_exps.items():
        print(f"Author {author} had {count} failed experiments")
    return experiments
