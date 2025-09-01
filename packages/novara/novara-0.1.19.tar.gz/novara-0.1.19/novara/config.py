from pydantic import BaseModel, Field
import yaml
from typing import Union, Optional, Literal
import logging
from datetime import datetime, timedelta

from novara.constants import CONFIG_FILE, CONFIG_HOME

logger = logging.getLogger("rich")


class Token(BaseModel):
    access_token: str = ''
    token_type: str = ''
    scope: str = ''
    expires_in: int = 0
    id_token: str = ''
    created_at:datetime = Field(default_factory=datetime.now)

    class Config:
        extra = 'ignore'

    @property
    def valide_until(self):
        return self.created_at + timedelta(seconds=self.expires_in)
    
    def is_valid(self):
        return self.access_token and self.token_type and self.valide_until > datetime.now()


class Config_Model(BaseModel):
    author:str = ''

    ssh_port:int = 22
    ssh_user:str = ''
    ssh_url:str = ''
    ssh_privatekey:str = ''

    server_url: str = ''

    idp_url:str = ''
    client_id:str = ''

    logging_level:Literal['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'] = 'NOTSET'

    token:Token = Token()

    class Config:
        extra = 'ignore'


class ConfigManager(Config_Model):
    is_initialized: bool = False

    def __init__(self, *args, **kwargs):
        object.__setattr__(self, 'is_initialized', False)       # avoid triggering loading logic
        if args or kwargs:
            super().__init__(*args, **kwargs)

    def _load(self) -> dict:
        logger.info('loading new config...')
        try:
            with open(CONFIG_FILE, 'r') as config_file:
                return yaml.safe_load(config_file)
        except (FileNotFoundError, OSError):
            logger.error('config file not found or not accessible')
            logger.debug('did you run novara configure?')
            exit()
            
    def _initialize(self):
        super().__init__(**self._load())
        self.is_initialized = True
    
    def raw_write(self, config: dict):
        try:
            if not CONFIG_HOME.exists():
                logger.info(f"creating directory {CONFIG_HOME}")
                CONFIG_HOME.mkdir()
            config_directory = CONFIG_FILE.parent
            if not config_directory.exists():
                logger.info(f"creating directory {config_directory}")
                config_directory.mkdir()
            with open(CONFIG_FILE, 'w') as config_file:
                yaml.dump(config, config_file)
        except OSError:
            logger.error("Couldn't create the config file it's not writable")
            exit()

    def update(self, **kwargs):
        """
        Update the configuration with new values.
        """

        for name, value in kwargs.items():
            if name in Config_Model.model_fields:
                setattr(self, name, value)
            else:
                logger.warning(f"Unknown configuration key: {name}")

        self.raw_write(self.model_dump())

    def save(self):
        self.raw_write(self.model_dump())

    def __getattr__(self, name: str):
        if name in Config_Model.model_fields:
            self._initialize()

        return super().__getattribute__(name)

    @property
    def raw_config(self):
        """Access the config as a dict"""
        if not self.is_initialized:
            self._initialize()
        return self.model_dump()

    @raw_config.setter
    def raw_config(self, value: Union[dict, BaseModel]):
        if isinstance(value, BaseModel):
            value = value.model_dump()

        if self.is_initialized:
            value = {**self.model_dump(), **value}

        super().__init__(**value)

config = ConfigManager()