import rich_click as click
from novara.utils import color_value, print, logger
from novara.config import config
from rich.table import Table, box
from novara.request import request


@click.command()
@click.option(
    "--container",
    "-c",
    default=None,
    help="specify container that the output should be filtered by",
)
def status(container):
    """get infos / status of currently running exploits"""

    logger.info(f'remote url: {config.server_url}')

    r = request.get("api/containers/")
    if not r.ok:
        raise click.ClickException(
            f"requesting status from remote failed with error:\n{r.text}"
        )

    status_infos = r.json()
    if (
        not any([status.get("container_id") == container for status in status_infos])
        and container is not None
    ):
        raise click.ClickException("No container with this id found")
        exit()

    # -----------------------------------------------------------------

    table = Table(title="container(s):", box=box.MINIMAL, highlight=True)

    table.add_column("Service:")
    table.add_column("Exploit:")
    table.add_column("Author:")
    table.add_column("Health:")
    table.add_column("Failing Percentage:")
    table.add_column("Starttime:")
    table.add_column("Container:")

    for info in status_infos:
        if container != None and (container in info["id"]):
            ...
        else:
            col_health = "green" if info["health"] == "healthy" else "red bold"

            table.add_row(
                f"[bold]{info['service']}[/]",
                f"[bold]{info['exploit']}[/]",
                f"{color_value(info['author'])}",
                f"[{col_health}]{info['health']}[/]",
                f"[bold]{info['failing_percentage']}[/]",
                f"{info['start_time'].split('.')[0].replace('T', ' ')}",
                f"[bold]{info['id'][:12]}[/]",
            )

    print(table)
