#!/usr/bin/env python3
# -*- coding: ascii -*-

"""
Filename: run.py
Author:   contact@simshadows.com

Entrypoint to starting simbot.
"""

import sys
from simbot.simbot_bootstrap import run

if __name__ == '__main__':
    if len(sys.argv) > 1:
        sys.exit(run(config_path=sys.argv[1]))
    else:
        sys.exit(run())

