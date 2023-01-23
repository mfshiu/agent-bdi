from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path

from holon import config

def init_logging():
    formatter = logging.Formatter(
        '%(levelname)1.1s %(asctime)s %(module)15s:%(lineno)03d %(funcName)15s) %(message)s',
        datefmt='%H:%M:%S')
    # formatter = logging.Formatter(
    #     '[%(levelname)1.1s %(process)5d-%(thread)11d %(asctime)s %(module)15s:%(lineno)03d %(funcName)15s] %(message)s',
    #     datefmt='%H:%M:%S')
    
    dir = "../_log"
    Path(dir).mkdir(parents=True, exist_ok=True)
    path = os.path.join(dir, "abdi.log")
    file_handler = TimedRotatingFileHandler(path, when="d")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(config.log_level)

def print_log(msg, ex=None):
    print("[%s] %s" % (str(datetime.now())[5:-3], msg))
    if ex:
        print(ex)
