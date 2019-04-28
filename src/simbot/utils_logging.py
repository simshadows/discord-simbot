"""
Filename: utils_logging.py
Author:   contact@simshadows.com

Helper utilities for logging, used throughout the project.
"""

import logging

LOGGER_PREFIX = "simbot"
_LOGGER_PREFIX_DOT = LOGGER_PREFIX + "." # Convenience


class NameLevelFilter(logging.Filter):
    """
    Enforces a minimum level on a particular section of the hierarchy.
    """

    def __init__(self, *args, **kwargs):
        self.level = kwargs.pop("level")
        self.inverse = kwargs.pop("inverse", False)
        super().__init__(*args, **kwargs)

    def filter(self, record):
        if self.inverse != super().filter(record): # Logical XOR
            return (record.levelno >= self.level)
        else:
            return True


def get_new_logger(s):
    if not (s.startswith(_LOGGER_PREFIX_DOT) or (s == LOGGER_PREFIX)):
        s = "simbot." + s
    return logging.getLogger(s)

def get_project_parent_logger():
    return logging.getLogger(LOGGER_PREFIX)


# String Parsing

_logger_levels = {
    "CRITICAL": logging.CRITICAL,
    "ERROR":    logging.ERROR,
    "WARNING":  logging.WARNING,
    "INFO":     logging.INFO,
    "DEBUG":    logging.DEBUG,
}

def safe_parse_logging_level(text):
    return _logger_levels[text.strip().upper()]

