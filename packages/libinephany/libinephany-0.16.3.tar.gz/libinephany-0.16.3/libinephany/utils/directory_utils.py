# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import os
from pathlib import Path

import yaml

# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def ensure_parent_directories_exist(local_path: str) -> None:
    """
    :param local_path: Local path to ensure the parent directories exist of.
    """

    as_path = Path(local_path)

    parent_directory = as_path.parent.absolute() if as_path.suffix else as_path.absolute()

    if not os.path.exists(parent_directory):
        os.makedirs(parent_directory)


def load_yaml(yaml_path: Path | str) -> dict | list:
    """
    :param yaml_path: Path to the YAML file to load.
    :return: YAML file loaded into a dictionary or list.
    """

    with open(yaml_path, "r") as file:
        config_data = yaml.safe_load(file)

    return config_data
