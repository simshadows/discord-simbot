"""
Filename: utils.py
Author:   contact@simshadows.com

Small routines and things frequently-used throughout the program.
"""

import os
import json
import re

################################################################################
# STRING PARSING ###############################################################
################################################################################

re_digits = re.compile("[0-9]+")

_true_strings  = {"true",  "yes", "y", "on",  "1", "set",   "ye" }
_false_strings = {"false", "no",  "n", "off", "0", "clear", "clr"}
assert _true_strings.isdisjoint(_false_strings)

def str_parse_boolean(text):
    """
    Returns True if the string says "TRUE" or any other known variation.
    Returns False if the string says "FALSE" or any other known variation.
    Returns None if the string is not known to represent any variation of
    "TRUE" or "FALSE".
    """
    text = text.strip().lower()
    if text in _true_strings:
        return True
    elif text in _false_strings:
        return False
    else:
        return None


################################################################################
# FILE I/O #####################################################################
################################################################################

_CWD = os.getcwd()
_ENCODING = "utf-8"

def json_read(relfilepath):
    with open(relfilepath, encoding=_ENCODING, mode="r") as f:
        return json.loads(f.read())

def json_write(relfilepath, *, data=None):
    mkdir_recursive(relfilepath)
    with open(relfilepath, encoding=_ENCODING, mode="w") as f:
        f.write(json.dumps(data, sort_keys=True, indent=4))
    return

def mkdir_recursive(relfilepath):
    absfilepath = os.path.join(_CWD, relfilepath)
    absdir = os.path.dirname(absfilepath)
    try:
        os.makedirs(absdir)
    except FileExistsError:
        pass
    return
