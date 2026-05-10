from pathlib import Path
import os

import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = Path("config/settings.yaml")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def get_env(name: str, required: bool = True):
    value = os.getenv(name)

    if required and not value:
        raise EnvironmentError(
            f"Missing required environment variable: {name}"
        )

    return value
