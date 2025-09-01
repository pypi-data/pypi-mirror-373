import rich_click as click
from novara.utils import logger
from novara.commands.generate import generate_dockerfile
import docker
import toml
from io import BytesIO
from zipfile import ZipFile
import os
import sys
from novara.request import request, JSONDecodeError
import json
import stat
import docker.models.containers
import subprocess
from docker.errors import BuildError

os_windows = os.name == "nt"

def build_image(*args, **kwargs):
    client = docker.from_env()

    kwargs.update({'decode':True, 'pull':True})

    response_stream:list[dict[str, str]] = client.api.build(*args, **kwargs)

    status_dict = {}

    for chunk in response_stream:
        type, *other_info = chunk.keys()
        match type:
            case 'error':
                raise BuildError(chunk['error'], response_stream)
            case 'errorDetail':
                sys.stdout.write(chunk)
            case 'stream':
                sys.stdout.write(chunk['stream'])
            case 'status':
                if 'id' in other_info:
                    change_id = chunk['id']
                    if not change_id in status_dict:
                        sys.stdout.write('\n')
                    status_dict.update({change_id:{'id':change_id, 'status':chunk['status'], 'progress':chunk.get('progress', '')}})
                    for _ in status_dict.keys():
                        sys.stdout.write('\033[F\033[K')
                    for update in status_dict.values():
                        sys.stdout.write(f"{update['id']}: {update['status']} {update.get('progress', '')}\n")
                else:
                    sys.stdout.write(chunk['status'])
            case 'aux':
                value = chunk['aux']
                if 'ID' in value:
                    image_id = value['ID'].split(':')[-1]
                else:
                    sys.stdout.write(f'{chunk}')
            case _:
                sys.stdout.write(f'{chunk}')

    image = None

    if image_id:
        image = client.images.get(image_id)

    return image

@click.group()
def run():
    """run a exploit script either locally or on remote"""

@run.command()
def shell():
    """run the exploit in your current shell"""
    try:
        with open("novara.toml", "r") as f:
            config_toml = toml.load(f)
    except (OSError, FileNotFoundError):
        raise click.ClickException("novara.toml either not there or unaccessable")
    if not 'sploit' in config_toml:
        raise click.ClickException("sploit needs to be specified in toml")
    if not 'script_name' in config_toml['sploit']:
        raise click.ClickException("sploit.script_name needs to be specified in toml")
    if not 'args' in config_toml['sploit']:
        raise click.ClickException("sploit.args needs to be specified in toml") 
    if not 'script_file' in config_toml:
        raise click.ClickException("script_name needs to be specified in toml") 

    start_sploit_script_path = os.path.join(os.getcwd(), config_toml['sploit']['script_name'])

    if not os_windows:
        file_mode = os.stat(start_sploit_script_path).st_mode
        if not file_mode & stat.S_IXUSR:
            logger.info("Setting the executable bit on `{}`".format(start_sploit_script_path))
            os.chmod(start_sploit_script_path, file_mode | stat.S_IXUSR)

    exploit_process = subprocess.Popen([os.path.join(os.getcwd(), config_toml['sploit']['script_name']), *config_toml['sploit']['args'], os.path.join(os.getcwd(), config_toml['script_file'])])

    try:
        exploit_process.wait()
    except KeyboardInterrupt:
        logger.warning("terminating exploit")
    exploit_process.kill()

@run.command()
def local():
    """run the exploit script locally"""
    client = docker.from_env()

    generate_dockerfile()

    logger.info("building image")
    image = build_image(path='.')

    logger.info("starting container")
    container: docker.models.containers.Container = client.containers.run(
        image, detach=True
    )
    try:
        for docker_log in container.logs(stream=True):
            click.echo(docker_log, nl=False)
    except KeyboardInterrupt:
        logger.warning("stopping container")
        container.kill()


@run.command()
@click.option(
    "-k",
    "--keep",
    default=False,
    is_flag=True,
    help="keep container, if it already exists",
)
@click.option(
    '-g',
    '--generate',
    default=False,
    is_flag=True,
    help="generate the dockerfile from the included toml file",
)
def remote(keep:bool, generate:bool):
    """upload and run the exploit on the remote server"""

    try:
        with open("novara.toml", "r") as f:
            toml_config = toml.load(f)
    except (OSError, FileNotFoundError):
        raise click.ClickException("novara.toml either not there or unaccessable")
    logger.info("read toml file")

    if "exploit_id" not in toml_config:
        raise click.ClickException(
            "no exploit_id in toml found, consider regenerating the toml with novara init"
        )

    exploit_id = toml_config.get("exploit_id")

    if not exploit_id:
        raise click.ClickException(
            "exploit_id is empty, consider regenerating the toml with novara init"
        )

    zip_archive = BytesIO()

    with ZipFile(zip_archive, "w") as zip:
        for root, _, filenames in os.walk(os.getcwd()):
            for name in filenames:
                zip.write(name, name)

    zip_archive.seek(0)

    logger.info("uploading zip...")

    r = request.post(f"api/exploits/{exploit_id}/", files={"file": zip_archive})
    if not r.ok:
        raise click.ClickException(f"Uploading zip failed with error: {r.text}")
        exit()

    if os.path.exists('Dockerfile') and not generate:
        try:
            with open("Dockerfile", "r") as f:
                docker_file = f.read()
        except (OSError, FileNotFoundError):
            raise click.ClickException("Dockerfile unaccessable")
        logger.info("read toml dockerfile")

        logger.warning('Using dockerfile to build container, use --generate to force rebuild from toml.')
        r = request.post(f"api/build/{exploit_id}/docker/", data=json.dumps(docker_file), stream=True)
        if not r.ok:
            raise click.ClickException(
                f"Failed building dockerfile file with error: {r.text}"
            )
        content_iterator = r.iter_lines()
        for line_str in content_iterator:
            line = json.loads(line_str)
            match line['type']:
                case 'logs':
                    sys.stdout.write(line['data'])
                case 'image':
                    image = line['data']
    else:
        try:
            with open("novara.toml", "r") as toml_file:
                toml_str = toml_file.read()
        except (FileNotFoundError, OSError):
            raise click.ClickException("Failed reading novara toml file")

        logger.info("building image...")

        r = request.post(f"api/build/{exploit_id}/toml/", data=json.dumps(toml_str), stream=True)
        if not r.ok:
            raise click.ClickException(
                f"Failed building novara toml file with error: {r.text}"
            )
            exit()

        logger.info(f'build logs:')

        content_iterator = r.iter_lines()
        for line_str in content_iterator:
            line = json.loads(line_str)
            match line['type']:
                case 'logs':
                    sys.stdout.write(line['data'])
                case 'image':
                    image = line['data']
    
    if image is None:
        raise click.ClickException("Something went wrong while building image")
        exit()

    logger.info(f"image: {image}")

    if not keep:
        logger.info(f"requesting removal of old containers of exploit: {exploit_id}")
        r = request.delete(f"api/exploits/container/{exploit_id}/")
        if r.status_code == 404:
            logger.info("No containers found for current exploit")
        if not r.ok:
            logger.warning(f"failed removing container with message: {r.text}")

    logger.info("starting new container...")

    r = request.post("api/containers/", params={"exploit_id": exploit_id})
    if not r.ok:
        raise click.ClickException(
            f"Failed starting new container with error: {r.text}"
        )
        exit()

    try:
        container_info = r.json()
    except JSONDecodeError:
        raise click.ClickException(
            f"failed to decode response as json: {r.text[:20] if len(r.text) > 20 else r.text}"
        )
    for info in container_info:
        logger.info(f"{info}: {container_info[info]}")

    logger.info(
        "Done deploying new container, to redeploy the container just run 'novara run remote' again"
    )
