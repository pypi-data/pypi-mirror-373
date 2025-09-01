import rich_click as click
import subprocess
import os
import time
from novara.utils import logger
from novara.constants import SSHKEY_FILE, SOCKET_FILE
from novara.config import config


def forward_docker_socket():
    if os.path.exists(SOCKET_FILE):
        os.remove(SOCKET_FILE)

    return subprocess.Popen(["ssh", "-i", SSHKEY_FILE, f"{config.ssh_user}@{config.ssh_url}", "-p", f"{config.ssh_port}", "-L", f"{SOCKET_FILE}:/var/run/docker.sock", "--", "sleep", "infinity"], stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

def cleanup_docker_socket(ssh:subprocess.Popen):
    ssh.kill()

    if os.path.exists(SOCKET_FILE):
        os.remove(SOCKET_FILE)


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.pass_context
def docker(ctx):
    """this command allows you to control the docker on the remote with the docker cli"""

    ssh = forward_docker_socket()
    
    env = {
        **os.environ.copy(),
        "DOCKER_HOST": f"unix://{SOCKET_FILE}",
    }

    try:
        while not os.path.exists(SOCKET_FILE):
            time.sleep(0.1)

        docker = subprocess.Popen(["docker", *ctx.args], env=env)
        
        docker.wait()
    except KeyboardInterrupt:
        logger.warning("terminating cli")
    docker.kill()
    cleanup_docker_socket(ssh)