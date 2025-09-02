import argparse
from pathlib import Path

from cuvette.scripts.get_jobs import get_job_data
from cuvette.scripts.utils import get_default_user, run_command

SSH_USER = "davidh"

# Host ai2-root
#     User davidh
#     Hostname phobos-cs-aus-452.reviz.ai2.in
#     IdentityFile ~/.ssh/id_rsa

CONFIG = """
Host {name}
    User {username}
    Hostname {hostname}
    Port {port}
    IdentityFile ~/.ssh/id_rsa
    ControlMaster auto
    ControlPath ~/.ssh/ai2locks/cm-%r@%h:%p
    ControlPersist yes
"""


def get_host(session_id=None):
    user = get_default_user()
    session_data = get_job_data(user, sessions_only=True)

    # Find the most recent session (sessions are already sorted by date)
    if not session_data:
        raise RuntimeError("No sessions found")

    session = None
    if session_id is not None:
        # Find the session with matching id
        for _session in session_data:
            if _session['id'] == session_id:
                session = _session
                break
    else:
        # Get most recent session, prioritizing GPU sessions
        gpu_sessions = [s for s in session_data if s.get('gpus') and int(s['gpus']) > 0]
        if gpu_sessions:
            session = gpu_sessions[-1]  # Most recent GPU session
        else:
            session = session_data[-1]  # Most recent session (CPU)
        
    if session is None:
        raise RuntimeError(f"No session found with id: {session_id}")
    
    host_name = session['hostname']
    
    if not host_name:
        raise RuntimeError("No hostname found for the most recent session")

    # Get all port mappings and display them
    print(f"Mapping ports for host: \033[35m{host_name}\033[0m")

    port_mappings = session['port_mappings']

    if not port_mappings:
        port_mappings = []
        raise ValueError("No port mappings found")
    
    # Convert port mappings from dict to list of tuples (remote_port, local_port)
    port_mappings = [(int(remote_port), int(local_port)) for local_port, remote_port in port_mappings.items()]
    
    for remote_port, local_port in port_mappings:
        print(f"{host_name}:{remote_port} (remote) -> localhost:{local_port} (local)")

    # Find server port
    server_port = None
    for remote_port, local_port in port_mappings:
        if local_port == 8080:
            server_port = remote_port

    if not server_port:
        raise RuntimeError("No mapping found for remote port 8080 on host ai2. See ~/.ssh/config.")

    return host_name, server_port

def update_ssh_config(host_name: str, server_port):
    # SSH config file path
    config_file = Path.home() / ".ssh" / "config"
    config_file.parent.mkdir(exist_ok=True)

    # Read existing config
    config_content = ""
    if config_file.exists():
        config_content = config_file.read_text()

    # Remove existing ai2 and ai2-root hosts from config
    config_lines = config_content.split('\n')
    new_config_lines = []
    skip_until_next_host = False
    
    for line in config_lines:
        if line.strip().startswith('Host ai2') or line.strip().startswith('Host ai2-root'):
            skip_until_next_host = True
            continue
        elif line.strip().startswith('Host ') and skip_until_next_host:
            skip_until_next_host = False
            new_config_lines.append(line)
        elif not skip_until_next_host:
            new_config_lines.append(line)
    
    config_content = '\n'.join(new_config_lines)

    # Remove ".reviz.ai2.in" from hostname
    host_name = host_name.replace(".reviz.ai2.in", "")

    # Add ai2 hosts
    config_content += CONFIG.format(name="ai2", username="root", hostname=host_name, port=server_port)
    config_content += CONFIG.format(name="ai2-root", username=SSH_USER, hostname=host_name, port=server_port)

    # Write updated config
    config_file.write_text(config_content)

    print(
        f"Updated SSH port to \033[35m{host_name}\033[0m:\033[31m{server_port}\033[0m in ~/.ssh/config for ai2 host."
    )


def open_ssh_tunnel():
    # Open SSH tunnel for fast connection
    socket_path = Path.home() / ".ssh" / "ai2locks"
    print(f"Opening SSH tunnel using lock {socket_path}")

    socket_path.mkdir(exist_ok=True)
    if socket_path.exists() and not socket_path.is_socket():
        import shutil

        shutil.rmtree(socket_path)
        socket_path.mkdir()

    # Open SSH connection
    run_command("ssh -MNf ai2")


def main():
    parser = argparse.ArgumentParser(description="Update SSH port configuration for Beaker session")
    parser.add_argument(
        "session_id", type=str, nargs="?", default=None, help="Beaker session ID to update port for"
    )
    args = parser.parse_args()

    host_name, server_port = get_host(args.session_id)
    update_ssh_config(host_name, server_port)
    open_ssh_tunnel()
