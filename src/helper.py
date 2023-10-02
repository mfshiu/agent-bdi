import os
from pathlib import Path

import logging
from logging.handlers import TimedRotatingFileHandler


logger = logging.getLogger("ABDI")
__log_init = False


def init_logging(log_dir, log_level=logging.DEBUG):
    formatter = logging.Formatter(
        '%(levelname)1.1s %(asctime)s %(module)15s:%(lineno)03d %(funcName)15s) %(message)s',
        datefmt='%H:%M:%S')
    
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_path = os.path.join(log_dir, "abdi.log")
    file_handler = TimedRotatingFileHandler(log_path, when="d")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger("ABDI")
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)    
    logger.setLevel(log_level)

    return logger


def get_logger():
    global __log_init
    global logger
    
    if not __log_init:
        logger = init_logging(log_dir="./_log")
        __log_init = True
        
    return logger
