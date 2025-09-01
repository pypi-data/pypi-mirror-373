import rich_click as click
from urllib.parse import urljoin, urlparse
import os
import requests
import logging
from novara.request import AuthSession
from novara.config import config, ConfigManager
from novara.utils import test_ssh_connection

from auto_click_auto import enable_click_shell_completion  

logger = logging.getLogger('rich')


@click.command()
@click.option(
    "--server_url",
    "-l",
    default=None,
    help="url to api-endpoint of your novara instance",
)
@click.option(
    "--author",
    "-a",
    default=None,
    help="to specify what author to use for the exploits",
)
@click.option(
    "--log-level",
    default="NOTSET",
    help="Change the log level of the logger (CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET)"
)
@click.option(
    "--auto-complete",
    is_flag=True,
    help="Enable auto-completion for the CLI commands",
)
def configure(server_url:str, author:str, log_level:str, auto_complete:bool):
    """conect to novara backend & configure the cli"""

    log_level = log_level.upper()

    if log_level not in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']:
        raise click.ClickException(f"invalid log level: {log_level}, must be one of: CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET")

    # Priority: CLI argument > Environment variable > Prompt

    logging.basicConfig(level=log_level)

    server_url = (
        server_url
        or os.environ.get("SERVER_URL")
        or click.prompt("Please enter the Novara server URL")
    )
    try:
        r = requests.get(urljoin(server_url, '/api/config/auth_config/'))
        if not r.ok:
            raise click.ClickException(f"the remote responded with error:\n{r.text}")
        
        local_config = ConfigManager.model_validate(r.json() | {'server_url': server_url, 'logging_level':log_level})

    except requests.JSONDecodeError:
        raise click.ClickException(f"unable to decode response as json:\n{r.text}")

    except requests.exceptions.ConnectionError:
        logger.error(f'failed to connect to backend. Is the url correct?')
        exit()

    
    session = AuthSession(local_config)

    userinfo = session.get_userinfo()

    if userinfo is None:
        logger.warning("failed to retrieve userinfo, please try again")

    local_config.author = (
        author
        or os.environ.get("AUTHOR_NAME")
        or (userinfo.preferred_username if userinfo else None)
        or (userinfo.given_name if userinfo else None)
        or click.prompt("Please enter your author username")
    )

    print('session configured')

    # -----------------------------------------------------------------

    r = session.get(urljoin(local_config.server_url, "/api/config/cli/"),
        params={'username':author}
    )
    if not r.ok:
        raise click.ClickException(f"the remote responded with error:\n{r.text}")

    # -----------------------------------------------------------------

    try:
        local_config.update(**r.json())
    except requests.JSONDecodeError:
        raise click.ClickException(f"unable to decode response as json:\n{r.text}")
    
    if auto_complete:
        enable_click_shell_completion('novara', verbose=log_level.lower() != 'debug')

    test_ssh_connection()