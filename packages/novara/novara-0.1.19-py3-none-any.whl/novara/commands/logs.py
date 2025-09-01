import rich_click as click
from novara.request import request, JSONDecodeError
from novara.utils import logger
import toml

@click.command()
@click.option("-e", "--exploit", default=None, help="specify a exploit id manually")
@click.option("-l", "--lines", default='50', help="specify the max amount of lines printed")
def logs(exploit, lines):
    """Request the logs of the exploit container"""
    try:
        with open("novara.toml", "r") as f:
            config = toml.load(f)
    except (OSError, FileNotFoundError):
        raise click.ClickException("novara.toml either not there or unaccessable")
    exploit_id = config['exploit_id']
    r = request.get('api/exploits/')
    if not r.ok:
        raise click.ClickException(
            f"failed requesting a list of exploits from remote with error: {r.text}"
        )
    try:
        exploits = r.json()
    except JSONDecodeError:
        raise click.ClickException(f"unable to decode response as json:\n{r.text}")

    current_exploit:dict|None = None

    for exploit in exploits:
        if exploit['id'] == exploit_id:
            current_exploit = exploit

    if current_exploit is None:
        raise click.ClickException(f'No exploit with id {exploit_id} found on remote')
    
    # console.print_json(data=current_exploit)
    logger.info(f'exploit: {current_exploit["service"]}-{current_exploit["name"]}')

    container_id = current_exploit.get('container_id')

    logger.info(f'container: {container_id}')

    if container_id is None:
        raise click.ClickException(f'No container found for exploit {exploit.get("name")}')
    
    r = request.get(f'api/containers/{container_id}/logs/')
    if not r.ok:
        raise click.ClickException(
            f"failed requesting a logs of container {container_id} from remote with error: {r.text}"
        )
    try:
        logs:str = r.json()
    except JSONDecodeError:
        raise click.ClickException(f"unable to decode response as json:\n{r.text}")
    
    max_lines = int(lines)

    total_lines = logs.count("\n")

    logger.info(f'displaying {min(max_lines, total_lines)} out of {total_lines} lines')

    if total_lines > max_lines:
        logs = '\n'.join(logs.split('\n')[-max_lines:])

    click.echo(logs)