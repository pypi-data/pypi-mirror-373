import rich_click as click
import os
import shutil
import stat

from io import BytesIO
from questionary import confirm, select, path
from zipfile import ZipFile

from novara.config import config
from novara.utils import logger
from novara.request import request, JSONDecodeError

def get_service():
    r = request.get("api/services/")
    if not r.ok:
        raise click.ClickException(
            f"Failed requesting list of services from remote with error: {r.text}"
        )

    try:
        services = r.json()
    except JSONDecodeError:
        raise click.ClickException(
            f"failed to decode response as json: {r.text[:20] if len(r.text) > 20 else r.text}"
        )

    service = select("Please select a service", choices=services).ask()

    if service is None:
        logger.warning('Cancelled by user, exiting...')
        exit()

    return service


@click.command()
@click.option(
    "-s",
    "--service",
    default=None,
    help="the name of the service the exploit will be attacking",
)
@click.option(
    "-n", "--name", default=None, help="the internal name for the exploit identifing it"
)
@click.option('-t', '--template-type', default=None, help=f'the type of the template', )
@click.option("-a", "--author", default=None, help="name of the exploit's author")
@click.option(
    "-d",
    "--directory",
    default=None,
    help="specify a different directory to put the exploit",
)
def init(service, name, template_type, author, directory):
    """Initialize a new exploit from a template"""

    # Priority: CLI argument > Environment variable > Prompt

    r = request.get('api/exploits/generate_name')
    if not r.ok:
        raise click.ClickException(
            f"Requesting name from remote failed with error: {r.text}."
        )
    
    name = name or r.json()

    
    r = request.get('api/services/template/types')
    if not r.ok:
        raise click.ClickException(
            f"Requesting template types from remote failed with error: {r.text}."
        )
    
    valide_template_types = r.json()

    service = service or get_service()
    author = (
        author
        or config.author
        or os.environ.get("AUTHOR")
        or click.prompt("Please enter this exploit author's name")
    )

    if author is None:
        logger.warning('Cancelled by user, exiting...')
        exit()

    type = (
        template_type 
        or os.environ.get("TEMPLATE-TYPE")
        or select(
            "Please select the type of the template",
            valide_template_types,
            default='generic'
        ).ask()
    )

    if type is None:
        logger.warning('Cancelled by user, exiting...')
        exit()

    if type not in valide_template_types:
        logger.error(
            f"Invalid template type '{template_type}'. Valid types are: {', '.join(valide_template_types)}"
        )
        return

    # -----------------------------------------------------------------

    if directory and directory[0] != "/":
        directory = os.path.join(os.getcwd(), directory)
    else:
        directory = path("Where should the exploied be saved to?", default=os.path.join(os.getcwd(), f'{service}-{name}'), only_directories=True).ask()
    
    if directory is None:
        logger.warning('Cancelled by user, exiting...')
        exit()

    if os.path.exists(directory) and len(os.listdir(directory)) > 0:
        logger.warning(f"The Path '{directory}' is not empty!")

        if confirm("Do you want to overwrite the directory?").ask():
            shutil.rmtree(directory)
        else:
            logger.info("Directory won't be overwritten, exiting...")
            exit()
    
    logger.info(f"setting up directory: {directory}")
    logger.info("requesting template")

    r = request.post(
        f"api/services/{service}/template/",
        params={"exploit_name": name, "exploit_author": author, "type":type, "additional_args": ""},
    )
    if not r.ok:
        raise click.ClickException(
            f"Requesting template from remote failed with error: {r.text}. Did you run novara configure?"
        )

    logger.info("extracting template")
    zip_template = BytesIO(r.content)
    os.mkdir(directory)
    
    with ZipFile(zip_template) as zip:
        for zip_info in zip.infolist():
            extracted_path = os.path.join(directory, zip_info.filename)
            if os.path.exists(extracted_path):
                if not confirm(f"'{zip_info.filename}' already exists. Do you want to overwrite it?", default=False).ask():
                    continue
            zip.extract(zip_info, directory)

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                os.chmod(os.path.join(root, file), 0o755)

    logger.info(f"Template extracted sucessfully into directory {directory or f'{service}-{name}'}")
    logger.info("To add a new dependency run 'novara generate'")
    logger.info("To run the current exploit run 'novara run [shell|local|remote]'")
    logger.info("Happy exploiting!")
