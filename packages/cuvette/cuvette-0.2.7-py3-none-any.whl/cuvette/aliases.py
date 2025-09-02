import argparse

from cuvette.scripts.utils import run_command


def ai2code():
    parser = argparse.ArgumentParser(description="Launch remote VSCode on ai2 host")
    parser.add_argument(
        "remote_path", nargs="?", default=None, help="Remote path to open (default: /root/ai2)"
    )

    args = parser.parse_args()

    if args.remote_path is None:
        cmd = "code --remote ssh-remote+ai2 /root/ai2"
    else:
        cmd = f"code --remote ssh-remote+ai2 /root/ai2/{args.remote_path}"

    stdout, stderr, returncode = run_command(cmd)
    if returncode != 0:
        raise RuntimeError(f"Failed to launch VSCode: {stderr}")
    return stdout


def ai2cursor():
    parser = argparse.ArgumentParser(description="Launch remote Cursor on ai2 host")
    parser.add_argument(
        "remote_path", nargs="?", default=None, help="Remote path to open (default: /root/ai2)"
    )

    args = parser.parse_args()

    if args.remote_path is None:
        cmd = "cursor --remote ssh-remote+ai2 /root/ai2"
    else:
        cmd = f"cursor --remote ssh-remote+ai2 /root/ai2/{args.remote_path}"

    stdout, stderr, returncode = run_command(cmd)
    if returncode != 0:
        raise RuntimeError(f"Failed to launch Cursor: {stderr}")
    return stdout


def ai2codereset():
    cmd = "ai2 'rm -rf ~/.vscode-server/cli/servers'"
    stdout, stderr, returncode = run_command(cmd)
    if returncode != 0:
        raise RuntimeError(f"Failed to reset VSCode server: {stderr}")
    return stdout


def ai2checks():
    cmd = "make type-check && make build && make style-check && make lint-check"
    stdout, stderr, returncode = run_command(cmd)
    if returncode != 0:
        raise RuntimeError(f"Checks failed: {stderr}")
    return stdout


def ai2cleanup():
    parser = argparse.ArgumentParser(description="Run code formatting and linting tools")
    parser.add_argument(
        "--fix", action="store_true", help="Fix issues automatically where possible"
    )

    args = parser.parse_args()

    if args.fix:
        cmd = "isort . && black . && ruff check . --fix && mypy ."
    else:
        cmd = "isort . && black . && ruff check . && mypy ."

    stdout, stderr, returncode = run_command(cmd)
    if returncode != 0:
        raise RuntimeError(f"Cleanup failed: {stderr}")
    return stdout


def ai2_ssh():
    cmd = "ssh ai2"
    stdout, stderr, returncode = run_command(cmd)
    if returncode != 0:
        raise RuntimeError(f"Failed to SSH into ai2: {stderr}")
    return stdout


def beaker_session_stop():
    parser = argparse.ArgumentParser(description="Launch remote Cursor on ai2 host")
    parser.add_argument(
        "session_name", nargs="?", default=None, help="Name of session to stop"
    )

    args = parser.parse_args()

    if args.session_name is not None:
        cmd = f"beaker session stop {args.session_name}"
    else:
        cmd = "beaker session stop"
    stdout, stderr, returncode = run_command(cmd)
    if returncode != 0:
        raise RuntimeError(f"Failed to stop beaker session: {stderr}")
    return stdout
