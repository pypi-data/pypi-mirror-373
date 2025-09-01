import rich_click as click
from novara.utils import logger
import os
import toml
from novara.request import request
from questionary import confirm


@click.command()
@click.option("-f","--force", default=False, is_flag=True, help="skip prompt")
@click.option("--directory", "-d", default="./", help="path to exploit")
def remove(directory, force):
    """remove the current running exploit"""
    
    directory = os.path.join(directory, "novara.toml")

    try:
        with open(directory, "r") as f:
            exploit_config = toml.load(f)
    except (OSError, FileNotFoundError):
        raise click.ClickException(f"{directory} either not there or unaccessable")

    if not force:
        confimation = confirm(f'Do you really want to stop exploit {exploit_config["service"]["name"]}-{exploit_config["exploit_name"]}').ask()
        if not confimation:
            logger.info('canceled stopping of exploit')
            exit()
    
    exploit_id = exploit_config["exploit_id"]

    logger.info("stopping container...")
    r = request.delete(f"api/exploits/{exploit_id}/")
    if not r.ok:
        raise click.ClickException(
            f"failed stopping container with message: {r.text}"
        )
    
    logger.info(f'Stopped exploit {exploit_config["service"]["name"]}-{exploit_config["exploit_name"]}')