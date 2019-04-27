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
import logging
import multiprocessing as mp
from copy import deepcopy

from .simbot import run as run_simbot

from .utils import json_read, json_write

logger = None # Configure later
buffered_warnings = []

_DEFAULT_CONFIG_PATH = "./config.json"

# Commented next to each key is the expected type. This type will be guaranteed
# by config_type_checks() and will ultimately be passed to the child process in
# the correct types.
# IMPORTANT: The config must not contain dictionaries within lists. This keeps things
#            nice and simple! :)
_DEFAULT_CONFIG_DICT = {
    "bot_login_token": "PLACEHOLDER", # (String)
    "bot_owner_id": "PLACEHOLDER",    # (String)
    "logging_level_override": None,   # (String | NULL)
    "paths": {
        "data_folder": "./data/",  # (String)
        "logfile": "./simbot.log", # (String)
    },
    "defaults": {
        "command_prefix": "/",               # (String)
        "status_message": "bot is running!", # (String)
    },
    "error_handling": {
        # If True, bot is automatically restarted after a full process crash.
        "automatic_restart_after_crash": True,     # (Boolean)
        # Forces errors to be reported to bot owners, overriding settings.
        "force_message_bot_owners_on_error": True, # (Boolean)
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
    Warns the user if there extra keys.
    Recursively checks dictionaries.
    """
    global buffered_warnings

    if not isinstance(config, dict):
        raise TypeError("Expecting a dict.")
    # All top-level keys must exist.
    for (k, v) in config.items():
        if k in default_config:
            if isinstance(default_config[k], dict):
                warn_extra_keys(v, default_config[k], key_list=key_list+[k,])
        else:
            # Prepare warning string
            buf = key_list + [k,]
            buf = [(f"\"{x}\"" if isinstance(x, str) else str(x)) for x in buf]
            # Issue warning string
            buf = "Extra key " + ":".join(buf) + " in configuration file."
            print(buf)
            buffered_warnings.append(buf)
    return

def setup_logging(level, log_filename):
    global logger
    global buffered_warnings

    if not ((level is None) or isinstance(level, str)):
        raise TypeError("Logging level must be a string or None.")
    if not isinstance(log_filename, str):
        raise TypeError("Log filename must be a string.")

    logger = logging.getLogger(None) # Get root Logger
    if not (level is None):
        all_levels = {
            "critical": logging.CRITICAL,
            "error":    logging.ERROR,
            "warning":  logging.WARNING,
            "info":     logging.INFO,
            "debug":    logging.DEBUG,
        }
        logger.setLevel(all_levels[level.strip().lower()])

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] (%(name)s) %(message)s")

    # File Handler
    fh = logging.FileHandler(log_filename)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Get module logger
    logger = logging.getLogger(__name__)

    logger.info("Logging initialized for simbot.")

    for s in buffered_warnings:
        logger.warning(s)
    buffered_warnings = None # Garbage collect the buffer
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

    print("Reading configuration file...")
    config = None
    if os.path.isfile(config_path):
        config = json_read(config_path)

        merge_default(config, _DEFAULT_CONFIG_DICT)
        warn_extra_keys(config, _DEFAULT_CONFIG_DICT)

        json_write(config_path, data=config)

        setup_logging(config["logging_level_override"], config["paths"]["logfile"])

        # Run the bot!

        reconnect_on_error = config["error_handling"]["automatic_restart_after_crash"]
        if not isinstance(reconnect_on_error, bool):
            raise TypeError("reconnect_on_error must be a Boolean.")

        logger.info("Bot starting.")
        while True:
            exitcode = run_simbot_in_worker_proc(config)
            if exitcode == 0:
                logger.info("Bot worker process terminated with exit code 0.")
                logger.info("Bot terminating normally.")
                break
            logger.warning(f"Bot worker process terminated with abnormal exit code {exitcode}.")
            if not reconnect_on_error:
                logger.warning("automatic_restart_after_crash is false. "
                        f"Bot terminating abnormally with exit code {exitcode}.")
                break
            logger.info("Reconnecting in 10 seconds.")
            time.sleep(10)
            logger.info("Bot restarting.")
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

