"""
Filename: utils.py
Author:   contact@simshadows.com

Small routines and things frequently-used throughout the program.
"""

import os
import json
import re

re_digits = re.compile("[0-9]+")

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
