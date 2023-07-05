from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path

from holon import config


def print_log(msg, ex=None):
    print("[%s] %s" % (str(datetime.now())[5:-3], msg))
    if ex:
        print(ex)
