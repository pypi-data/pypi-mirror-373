import rich_click as click
from novara.constants import __version__
from novara.utils import logger, test_ssh_connection
from novara.config import config
from novara.request import request
from novara.constants import SOCKET_FILE
from novara.commands.docker import forward_docker_socket, cleanup_docker_socket, docker
import requests
import time
import subprocess
import os


from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

def get_latest_version():
    url = f"https://pypi.org/pypi/novara/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        latest_version = data['info']['version']
        return latest_version
    else:
        raise Exception(f"Failed to fetch package information: {response.status_code}")

@click.command()
def info():
    logger.debug('fetching version of the cli from pypi...')
    latest_version = get_latest_version()

    logger.debug("check connectivity to the backend...")
    try:
        r = request.get("api/up")
        is_up = r.status_code == 200
    except Exception:
        is_up = False

    if is_up:
        logger.debug("time response of the backend...")
        start_time = time.time()
        r = request.get("api/up")
        time_elapsed = time.time() - start_time
    else:
        time_elapsed = None

    logger.debug('Testing ssh connection...')
    test_ssh_connection()

    logger.debug('Testing connection to docker daemon...')
    ssh = forward_docker_socket()

    time.sleep(0.5)

    docker_version_string = None
    docker_error = None
    try:
        # Set DOCKER_HOST to point to the forwarded socket
        os.environ["DOCKER_HOST"] = f'unix://{SOCKET_FILE}'
        result = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_output = result.stdout.strip()
            # Try to get platform name as well
            platform_result = subprocess.run(
                ["docker", "version", "--format", "{{.Server.Platform.Name}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            platform_name = platform_result.stdout.strip() if platform_result.returncode == 0 else "Docker Engine"
            docker_version_string = f"{platform_name} {version_output}"
        else:
            raise Exception(result.stderr.strip())
    except Exception as e:
        docker_error = str(e)

    cleanup_docker_socket(ssh)

    console = Console()

    # Header
    console.rule("[bold cyan]Novara CLI Info[/bold cyan]", style="cyan")

    # Version Info
    version_table = Table(show_header=False, box=None)
    version_table.add_row("Novara CLI Version:", f"[green]{__version__}[/green]")
    version_table.add_row("Latest Available:", f"[green]{latest_version}[/green]")
    console.print(version_table)

    if __version__ != latest_version:
        console.print(
            Panel.fit(
                Text(
                    "You are using an older version of the CLI.\n"
                    "Consider upgrading:\n"
                    "    pip install --upgrade novara",
                    style="yellow bold"
                ),
                border_style="yellow"
            )
        )

    # Backend Info
    backend_table = Table(show_header=False, box=None)
    backend_table.add_row("Backend Server:", f"[blue]{config.server_url}[/blue]")
    backend_table.add_row("Author:", f"{config.author}")
    if is_up and time_elapsed is not None:
        backend_table.add_row("Backend Status:", f"[green]Reachable ({time_elapsed:.2f}s response)[/green]")
    else:
        backend_table.add_row("Backend Status:", "[red]Unreachable[/red]")
    console.print(backend_table)

    # Docker Info
    docker_table = Table(show_header=False, box=None)
    if docker_version_string:
        docker_table.add_row("Docker Daemon:", f"[green]{docker_version_string}[/green]")
    elif docker_error:
        docker_table.add_row("Docker Daemon:", f"[red]Failed to connect ({docker_error})[/red]")
    console.print(docker_table)

    # SSH Info
    ssh_table = Table(show_header=False, box=None)
    ssh_table.add_row("[bold]SSH Server Info:[/bold]", "")
    ssh_table.add_row("  URL:", f"{config.ssh_url}")
    ssh_table.add_row("  Port:", f"{config.ssh_port}")
    ssh_table.add_row("  Username:", f"{config.ssh_user}")
    console.print(ssh_table)

    console.rule(style="cyan")
