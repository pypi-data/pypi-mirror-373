import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, Tuple, Type

from pydantic import BaseModel

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    TomlConfigSettingsSource,
    EnvSettingsSource,
)

from blocks_cli.config.auth import AuthConfig

class ClientConfig(BaseModel):
    client_url: str = "https://api.prod.blocksorg.com/client"
    orchestrator_url: str = "https://api.prod.blocksorg.com"

class Config(BaseSettings):
    env: str = "prod"
    auth: AuthConfig = AuthConfig()
    clients: ClientConfig = ClientConfig()

    @staticmethod
    def get_config_file() -> Path:
        return Config.get_config_dir() / 'config.toml'

    @staticmethod
    def get_config_dir() -> Path:
        """Get the configuration directory for the blocks CLI."""
        # Use platform-specific user config directory
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / 'blocks'
        else:  # Unix/Linux/MacOS
            config_dir = Path.home() / '.config' / 'blocks'
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @classmethod
    def settings_customise_sources(
        cls, settings_cls: Type[BaseSettings], **kwargs
    ) -> Tuple[EnvSettingsSource, PydanticBaseSettingsSource]:
        return (
            EnvSettingsSource(settings_cls, env_prefix='BLOCKS_', env_nested_delimiter='__'),
            TomlConfigSettingsSource(settings_cls, toml_file=Config.get_config_file()),
        )

config = Config()
