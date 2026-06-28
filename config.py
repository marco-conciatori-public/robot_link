"""
Shared YAML-based config loader for both robot computers.

Priority, highest wins: Python kwargs > CLI args (--key value) > YAML file > hardcoded
defaults. This matches the project convention and Marco's IDE workflow: running a script
with zero CLI arguments must work (everything is read from the YAML file), and CLI args are
only overrides layered on top.

A call supplies either an explicit ``yaml_path`` or a ``caller_name`` (the calling script's
``__file__``, resolved to ``<config_folder>/<stem>.yaml``). If the file is not found, the
loader walks up a few parent directories before giving up, so a script behaves the same
whether it was launched from the project root or from its own folder.

Each repo wraps this with a thin local ``args.py`` shim that injects its own
``CONFIG_FOLDER_PATH`` as ``config_folder``, so this module stays repo-agnostic.
"""

import copy
import argparse
from pathlib import Path

import yaml

from . import common

_MAX_PARENT_WALK = 5


def import_args(yaml_path: str = None,
                caller_name: str = None,
                config_folder: str = None,
                read_from_command_line: bool = False,
                **kwargs) -> dict:
    assert caller_name is not None or yaml_path is not None, 'Either yaml_path or caller_name must be supplied'
    assert caller_name is None or yaml_path is None, 'Only one of yaml_path or caller_name can be supplied'
    if caller_name is not None:
        file_stem = Path(caller_name).resolve().stem
        prefix = config_folder if config_folder is not None else ''
        yaml_path = f'{prefix}{file_stem}.yaml'

    level_up = 0
    data_dict = None
    while data_dict is None:
        try:
            with open(yaml_path) as f:
                data_dict = yaml.safe_load(f)
        except FileNotFoundError:
            print(f'File "{yaml_path}" not found. Trying to go up one level...')
            if level_up == _MAX_PARENT_WALK:
                raise
            level_up += 1
            yaml_path = '../' + yaml_path

    if read_from_command_line:
        # command line arguments have priority over yaml arguments
        data_dict = from_command_line(default_data_dict=data_dict)

    # function arguments have priority over yaml AND command line arguments
    data_dict = from_function_arguments(default_data_dict=data_dict, **kwargs)

    if isinstance(data_dict, dict) and data_dict.get('verbose', 0) >= 3:
        print(f'Yaml config file: "{yaml_path}"')
        print('Imported parameters:')
        common.pretty_print_dict(data_dict)

    return data_dict


def from_command_line(default_data_dict: dict) -> dict:
    parser = argparse.ArgumentParser()
    for key in default_data_dict:
        value = default_data_dict[key]
        parser.add_argument(f'--{key}', dest=key, type=type(value))

    updated_data_dict = copy.deepcopy(default_data_dict)
    parsed = vars(parser.parse_args())
    for key in parsed:
        if parsed[key] is not None:
            updated_data_dict[key] = parsed[key]

    return updated_data_dict


def from_function_arguments(default_data_dict: dict, **kwargs) -> dict:
    updated_data_dict = copy.deepcopy(default_data_dict)
    for key in kwargs:
        updated_data_dict[key] = kwargs[key]

    return updated_data_dict
