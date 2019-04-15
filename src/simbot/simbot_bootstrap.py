"""
Filename: simbot_bootstrap.py
Author:   contact@simshadows.com

Manages basic configuration, and wraps simbot in a child process that is restarted
automatically by this module as needed.
"""

import os
import os.path
import sys
import time
import textwrap
import multiprocessing as mp
from copy import deepcopy

from .simbot import run as run_simbot

from .utils import json_read, json_write

_DEFAULT_CONFIG_PATH = "./config.json"

# IMPORTANT: The config must not contain dictionaries within lists. This keeps things
# nice and simple! :)
_DEFAULT_CONFIG_DICT = {
    "bot_login_token": "PLACEHOLDER",
    "bot_owner_id": "PLACEHOLDER",
    "paths": {
        "data_folder": "./data/",
        "logs": "./data/logs/",
    },
    "defaults": {
        "command_prefix": "/",
        "status_message": "bot is running!",
    },
    "error_handling": {

        # If True, bot is automatically restarted after a full process crash.
        "automatic_restart_after_crash": True,

        # Forces errors to be reported to bot owners, overriding settings.
        "force_message_bot_owners_on_error": True,

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
    Carries out primitive type checks. Raises exceptions if types are wrong.

    IMPORTANT: This method will only guarantee primitive types (e.g. strings, ints),
    but will NOT guarantee checking of data (e.g. negative ints, strings representing
    Discord user IDs, and whether or not a list contains at least one value). Further
    data validation must be carried out down the line.
    """
    obj = config["bot_login_token"]
    if not isinstance(obj, str):
        raise TypeError("Bot login token must be a string.")
    obj = config["bot_owner_id"]
    if not isinstance(obj, str):
        raise ValueError("Bot owner user ID must be a string.")

    obj = config["paths"]["data_folder"]
    if not isinstance(obj, str):
        raise TypeError("Data folder path must be a string.")
    obj = config["paths"]["logs"]
    if not isinstance(obj, str):
        raise TypeError("Logs folder path must be a string.")

    obj = config["defaults"]["command_prefix"]
    if not isinstance(obj, str):
        raise TypeError("Command prefix must be a string.")
    obj = config["defaults"]["status_message"]
    if not isinstance(obj, str):
        raise TypeError("Status message must be a string.")

    obj = config["error_handling"]["automatic_restart_after_crash"]
    if not isinstance(obj, bool):
        raise TypeError("automatic_restart_after_crash must be a boolean.")
    obj = config["error_handling"]["force_message_bot_owners_on_error"]
    if not isinstance(obj, bool):
        raise TypeError("force_message_bot_owners_on_error must be a boolean.")
    return

def run_simbot_in_worker_proc(config):
    config = deepcopy(config)
    # A child process editing the config dict probably won't do much, but better to
    # be a bit safe?
    def child_entrypoint():
        sys.exit(run_simbot(config))

    proc = mp.Process(target=child_entrypoint, daemon=True)
    proc.start()
    proc.join()
    return proc.exitcode

def run(config_path=_DEFAULT_CONFIG_PATH):
    exitcode = 1 # An error by default.

    print("Reading configuration file...") # TODO: log?
    config = None
    if os.path.isfile(config_path):
        config = json_read(config_path)

        merge_default(config, _DEFAULT_CONFIG_DICT)
        warn_extra_keys(config, _DEFAULT_CONFIG_DICT)
        config_type_checks(config)

        # Save config file
        json_write(config_path, data=config)

        # Run the bot!
        reconnect_on_error = config["error_handling"]["automatic_restart_after_crash"]
        assert isinstance(reconnect_on_error, bool)
        while True:
            print("Starting the bot...")
            exitcode = run_simbot_in_worker_proc(config)
            print(f"Bot worker process terminated. Exit code {exitcode}.")
            if exitcode == 0:
                print("Bot will terminate normally.")
                break
            if not reconnect_on_error:
                print("automatic_restart_after_crash is false. "
                        "Bot will terminate abnormally.")
                break
            print("Abnormal exit. Reconnecting in 10 seconds.")
            time.sleep(10)
            print("Attempting to restart...")
    else:
        config = _DEFAULT_CONFIG_DICT
        # Save config file
        json_write(config_path, data=config)
        print(f"Created config file {config_path}. Please edit this and run again!")
        buf = textwrap.dedent("""
                This appears to be your first time setting up this bot.

                Please edit the following items in in config.ini before relaunching:
                    bot_login_token
                    bot_owner_id
                """).strip()
        print(buf)
        exitcode = 0

    return exitcode

