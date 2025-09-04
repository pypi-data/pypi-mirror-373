import typing as t
from pathlib import Path

import yaml

from meili_sdk.config.type import Config

__all__ = (
    "load_config",
    "safe_load_config",
)


def load_config() -> Config:
    config_path = Path.home().joinpath(".meili", "cfg.yaml")

    with open(config_path, "r") as cfg_file:
        config = yaml.safe_load(cfg_file)
        return config


def safe_load_config() -> t.Optional[Config]:
    try:
        return load_config()
    except (FileNotFoundError, yaml.YAMLError):
        pass
