from pathlib import Path
import os
from importlib.metadata import version

__version__ = version('novara')

CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser()
CONFIG_FILE = CONFIG_HOME / "novara" / "config.yml"
SSHKEY_FILE = CONFIG_HOME / "novara" / "novara.key"
SOCKET_FILE = CONFIG_HOME / "novara" / "novara_docker.sock"