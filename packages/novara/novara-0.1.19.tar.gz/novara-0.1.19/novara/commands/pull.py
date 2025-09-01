import rich_click as click
from novara.request import request, JSONDecodeError
from novara.utils import logger
from questionary import confirm, select
from io import BytesIO
from zipfile import ZipFile
import os
import shutil
import toml

def delete_all_in_directory(directory_path):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

def download_empty_template(exploit_id:str):

    r = request.get('api/exploits/')
    if not r.ok:
        raise click.ClickException(
            f"Requesting exploits from remote failed with error: {r.text}. Did you run novara configure?"
        )
    
    try:
        exploits = r.json()
    except JSONDecodeError:
        raise click.ClickException(f"unable to decode response as json:\n{r.text}")
    
    service = None

    for exploit in exploits:
        if exploit['id'] == exploit_id:
            service = exploit['service']

    if service is None:
        raise click.ClickException(f'exploit with id {exploit_id} not found on remote')

    r = request.post(
        f"api/services/{service}/template/",
        params={"exploit_id": exploit_id, "exploit_name":'', "exploit_author": ""},
    )
    if not r.ok:
        raise click.ClickException(
            f"Requesting template from remote failed with error: {r.text}. Did you run novara configure?"
        )
    return r

def download_exploit(exploit_id: str, exploit_name: str, dir:str, files:list[str], is_current_dir:bool=False):
    version = -1

    if files is not None:
        if len(files):
            choices = [str(x+1) for x in range(len(files))]
            choices[0] = f'{choices[0]} (initial)'
            choices[-1] = f'{choices[-1]} (latest)'

            selected = select('Please select a version:', choices=choices[::-1]).ask()
            version = choices.index(selected)
        else:
            logger.warning('no version found')

    if dir is None:
        dir = os.path.normpath(os.path.join(os.getcwd(), exploit_name))
    logger.info(f"exploit id: {exploit_id}")
    logger.info("requesting exploit")

    r = request.get(f"api/exploits/{exploit_id}/", params={'version':version})
    if not r.ok:
        if 'no files' in r.text:
            logger.info("The requested exploit doesn't yet have any files yet.")
            result = confirm('Do you want to download a empty template?').ask()
            if result:
                r = download_empty_template(exploit_id)
        
        else:
            raise click.ClickException(
                f"Requesting exploit from remote failed with error: {r.text}. Did you run novara configure?"
            )
    logger.info("extracting exploit")
    zip_template = BytesIO(r.content)
    if os.path.exists(dir):
        overwrite = is_current_dir or confirm(
            message=f"Do you want to overwrite the directory '{dir}'? (Y/n)",
            default=True
        ).ask()
        if not overwrite:
            raise click.ClickException(
                "Directory already exists and can't be overwritten. Consider using the -d or --dir to specify a different directory."
            )
            exit()
        delete_all_in_directory(dir)
    else:
        os.mkdir(dir)
    with ZipFile(zip_template) as zip:
        zip.extractall(dir)

    logger.info("Exploit extracted sucessfully")


@click.command()
@click.option(
    "-s", "--service", default=None, help="name of the service the exploit is targeting"
)
@click.option("-n", "--name", default=None, help="full name of the exploit to pull")
@click.option(
    "-d",
    "--directory",
    default=None,
    help="specify a different directory to save the exploit",
)
@click.option("-l", "--listall", default=False, help="list all exploits", is_flag=True)
@click.option("-v", "--version", default=False, help="select a version (pulls latest version by default)", is_flag=True)
@click.argument("pull_name", required=False)
def pull(service, name, directory, listall, version, pull_name):
    """Pull existing exploits from novara, if no other arguments are provided and there is a novara.toml in the same directory the cli will try to pull the newest version of the exploit"""
    
    r = request.get("api/exploits/")
    if not r.ok:
        raise click.ClickException(
            f"failed requesting a list of exploits from remote with error: {r.text}"
        )
    try:
        exploits:list[dict] = r.json()
    except JSONDecodeError:
        raise click.ClickException(f"unable to decode response as json:\n{r.text}")
    
    name = name or pull_name

    exploit = None
    exploit_config = None
    if service is None and name is None and directory is None and not listall:
        try:
            with open("novara.toml", "r") as f:
                exploit_config = toml.load(f)
        except (OSError, FileNotFoundError):
            listall = True
    if not exploit_config is None:
        exploit_id = exploit_config.get('exploit_id')
        for e in exploits:
            if e['id'] == exploit_id:
                exploit = e
                break

    if exploit is not None:         
        download_exploit(exploit['id'], f"{exploit['service']}-{exploit['name']}", os.getcwd(), files=exploit.get('files', []) if version else None, is_current_dir=True)
        exit()

    # -----------------------------------------------------------------

    # check if any exploits are even available
    if not len(exploits):
        raise click.ClickException("No exploits to pull!")

    # pull by name ----------------------------------------------------
    if name and any(exploit["name"] == name or f'{exploit["service"]}-{exploit["name"]}' == name for exploit in exploits):
        exploit = None
        for exploit in exploits:
            if exploit["name"] == name or f'{exploit["service"]}-{exploit["name"]}' == name:
                exploit = exploit
                break
        download_exploit(exploit["id"], name, directory, files=exploit.get('files', []) if version else None)
        exit()
    elif name:
        raise click.ClickException(f"No exploits named '{name}' available!")

    # chose a service -------------------------------------------------

    if listall:
        # pull by selection ----------------------------------------
        identifier = select(
            "Chose a exploit:",
            choices=[f'{e["service"]}-{e["name"]}' for e in exploits],
        ).ask()

        if identifier is None:
            exit()

        for exploit in exploits:
            if f'{exploit["service"]}-{exploit["name"]}' == identifier:
                download_exploit(exploit['id'], identifier, directory, files=exploit.get('files', []) if version else None)
                exit()
    
    elif service is None:
        services = []
        for exploit in exploits:
            if not exploit['service'] in services:
                services.append(exploit['service'])
        service = select(
                "Please select a service:",
                choices=services,
            ).ask()
        
        if service is None:
            logger.warning('canceling pull')
            return

    # pull by service -------------------------------------------------
    if service and any(exploit["service"] == service for exploit in exploits):
        service_exploits:dict[dict] = {}
        for exploit in exploits:
            if exploit["service"] == service:
                service_exploits[exploit["name"]] = exploit

        if len(list(service_exploits.keys())) > 1:
            service = select(
                "there are multiple exploits available for this service, please select one:",
                choices=list(service_exploits.keys()),
            ).ask()
            if service is None:
                logger.warning('canceling pull')
                return
            exploit = service_exploits[service]
        else:
            exploit = list(service_exploits.values())[0] 
        
        download_exploit(exploit["id"], f"{exploit['service']}-{exploit['name']}", directory, files=exploit.get('files', []) if version else None)
        exit()

    elif name:
        raise click.ClickException(f"No exploits for '{service}' available")
