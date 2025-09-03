import tomli
import tomli_w
from pathlib import Path
from repopi.utils.config import Config

CONFIG_FILE_PATH = Path.home() / ".repopi.toml"

def get_config_path() -> Path:
    return CONFIG_FILE_PATH

def load_config() -> Config:
    if not get_config_path().exists():
        return Config()

    with open(get_config_path(), "rb") as f:
        try:
            data = tomli.load(f)
            return Config(**data)
        except (tomli.TOMLDecodeError, TypeError, ValueError):
            return Config()

def save_config(config: Config):
    with open(get_config_path(), "wb") as f:
        tomli_w.dump(config.dict(), f)
