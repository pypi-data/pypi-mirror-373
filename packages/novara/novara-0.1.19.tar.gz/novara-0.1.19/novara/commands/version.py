import rich_click as click

from novara.utils import logger

@click.command()
def version():
    """Display the current version of the CLI."""
    from novara.constants import __version__

    logger.info(f"Current CLI version: {__version__}")
    logger.info("For more information, visit https://github.com/TeamM0unt41n/novara")
    logger.info("For help, use the command: novara --help")