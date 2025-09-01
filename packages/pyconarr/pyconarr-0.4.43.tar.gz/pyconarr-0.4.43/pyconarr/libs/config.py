from importlib import metadata

import yaml


def get_version():
    return metadata.version("pyconarr")


with open("config/pyconarr.yml", "r") as f:
    config = yaml.safe_load(f)
