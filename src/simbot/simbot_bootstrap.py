"""
Filename: simbot_bootstrap.py
Author:   contact@simshadows.com

Manages basic configuration, and wraps simbot in a child process that is restarted
automatically by this module as needed.
"""

import os
import os.path 
from copy import deepcopy

from .simbot import run as run_simbot

from .utils import json_read, json_write, re_digits

_DEFAULT_CONFIG_PATH = "./config.json"

_DEFAULT_CONFIG_DICT = {
    "bot_login_token": "PLACEHOLDER",
    "bot_owners_ids": [
        "PLACEHOLDER",
    ],
    "paths": {
        "data_folder": "./data/",
        "logs": "./data/logs/",
    },
    "defaults": {
        "command_prefix": "/",
        "status_message": "bot is running!",
    },
    #"options": {
    #    #TODO
    #}
}

def merge_default(config, default_config):
    """
    Any missing keys are added with default values.
    Recursively checks dictionaries.
    """
    if not isinstance(config, dict):
        raise TypeError("Expecting a dict.")
    for (k, v) in default_config.items():
        if k not in config:
            config[k] = deepcopy(v)
        elif isinstance(v, dict):
            merge_default(config[k], v)
    return

def warn_extra_keys(config, default_config, key_list=[]):
    """
    Warns the user if there are extra keys.
    """
    if not isinstance(config, dict):
        raise TypeError("Expecting a dict.")
    # All top-level keys must exist.
    for (k, v) in config.items():
        if k in default_config:
            if isinstance(default_config[k], dict):
                warn_extra_keys(v, default_config[k], key_list=key_list+[k,])
        else:
            # Prepare feedback string
            buf = key_list + [k,]
            buf = [(f"\"{x}\"" if isinstance(x, str) else str(x)) for x in buf]
            # Issue warning
            print("WARNING: Extra key " + ":".join(buf) + " in config.")
            # TODO: LOG THIS.
    return

def config_type_checks(config):
    """
    Raises exceptions if types are wrong.
    """
    if not isinstance(config["bot_login_token"], str):
        raise TypeError("Bot login token must be a string.")
    if not all(re_digits.fullmatch(x) for x in config["bot_owners_ids"]):
        raise ValueError("Bot owner user IDs must be strings of digit characters only.")

    if not isinstance(config["paths"]["data_folder"], str):
        raise TypeError("Data folder path must be a string.")
    if not isinstance(config["paths"]["logs"], str):
        raise TypeError("Logs folder path must be a string.")

    if not isinstance(config["defaults"]["command_prefix"], str):
        raise TypeError("Command prefix must be a string.")
    if not isinstance(config["defaults"]["status_message"], str):
        raise TypeError("Status message must be a string.")
    return

def run(config_path=_DEFAULT_CONFIG_PATH):
    # Read config file
    config = None
    if os.path.isfile(config_path):
        config = json_read(config_path)

        merge_default(config, _DEFAULT_CONFIG_DICT)
        warn_extra_keys(config, _DEFAULT_CONFIG_DICT)
        config_type_checks(config)

        # Save config file
        json_write(config_path, data=config)

        # Run the bot!
        run_simbot(config)
        # TODO: Wrap in a child process!
    else:
        config = _DEFAULT_CONFIG_DICT
        # Save config file
        json_write(config_path, data=config)
        print(f"Created config file {config_path}. Please edit this and run again!")

    return 0

