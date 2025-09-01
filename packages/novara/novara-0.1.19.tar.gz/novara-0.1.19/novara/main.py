from rich import traceback

# traceback.install(show_locals=True)

import rich_click as click
from novara.commands.init import init
from novara.commands.status import status
from novara.commands.configure import configure
from novara.commands.pull import pull
from novara.commands.docker import docker
from novara.commands.generate import generate
from novara.commands.run import run
from novara.commands.logs import logs
from novara.commands.stop import stop
from novara.commands.remove import remove
from novara.commands.info import info 
from novara.commands.version import version


@click.group()
def main():
    """novara is a cli tool to help in A/D CTFs"""


main.add_command(init)
main.add_command(configure)
main.add_command(status)
main.add_command(pull)
main.add_command(docker)
main.add_command(generate)
main.add_command(run)
main.add_command(logs)
main.add_command(stop)
main.add_command(remove)
main.add_command(info)
main.add_command(version)