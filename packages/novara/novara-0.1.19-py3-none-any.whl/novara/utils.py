from rich.console import Console
from rich.logging import RichHandler
from random import randrange, seed
import logging
import os
from novara.config import config
from novara.constants import SSHKEY_FILE
from novara.request import AuthSession
import paramiko

# -----------------------------------------------------------------

logging.basicConfig(
    level=config.logging_level if config.is_initialized else 'NOTSET',
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger("rich")
console = Console()

# -----------------------------------------------------------------


def print(*args, **kwargs):
    console.print(*args, **kwargs)


# -----------------------------------------------------------------


def color_value(value: str):
    seed(value.lower())
    r, g, b = [str(hex(randrange(25, 255))[2:]) for _ in range(3)]
    value_colored = f"[bold #{r}{g}{b}]{value}[/]"

    return value_colored


# -----------------------------------------------------------------

def test_ssh_connection():
    # --------------
    try:
        with open(SSHKEY_FILE, "w") as f:
            f.write(config.ssh_privatekey)
    except OSError:
        logger.error("Couldn't create the SSH-key it's not writable")
        exit()
    # --------------
    try:
        os.chmod(SSHKEY_FILE, 0o600)
    except OSError:
        logger.error("Couldn't change the SSH-key's permissions")
        exit()
    # --------------
    logger.info("Testing SSH connection...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        private_key = paramiko.RSAKey.from_private_key_file(SSHKEY_FILE)
        ssh.connect(
            hostname=config.ssh_url,
            port=config.ssh_port,
            username=config.ssh_user,
            pkey=private_key,
            timeout=10
        )
        stdin, stdout, stderr = ssh.exec_command("echo :3")
        error_output = stderr.read().decode().strip()

        # Check if there was any error output
        if error_output:
            logger.error("Failed to establish SSH connection!!!")
            logger.debug("Is the public key on the target's authorized_keys file?")
            logger.error(error_output)
            return False

        logger.info("SSH connection successful")
        return True

    except paramiko.SSHException as e:
        logger.error("Failed to establish SSH connection!!!")
        logger.error(f"SSHException: {e}")
        return False

    except Exception as e:
        logger.error("An unexpected error occurred while trying to connect via SSH.")
        logger.error(f"Exception: {e}")
        return False

    finally:
        ssh.close()