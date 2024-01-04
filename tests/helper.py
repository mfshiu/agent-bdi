import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import re
from pathlib import Path

from abdi_config import LOGGER_NAME


__logger = logging.getLogger(LOGGER_NAME)
__log_init = False


def out(text:str):
    if os.name == 'nt':
        text = text.encode('cp950', "ignore")
        text = text.decode('cp950')
    return text


def ensure_directory(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
        __logger.info(f"Directory '{dir_path}' created successfully.")


def get_config():
    with open("app_config.json", 'r') as file:
        _ = json.load(file)
    return _
    
    
def get_logger():
    global __log_init
    global __logger
    
    if not __log_init:
        __log_init = True
        
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR
        }
        _ = get_config()
        log_level = logging.DEBUG
        if "log_level" in _:
            if _["log_level"] in log_levels:
                log_level = log_levels[_["log_level"]]            
            __logger = _init_logging(_.get("log_path"), log_level)
        
    return __logger


def _init_logging(log_path:str, log_level):
    formatter = logging.Formatter(
        '%(levelname)1.1s %(asctime)s %(module)15s:%(lineno)03d %(funcName)15s) %(message)s',
        datefmt='%H:%M:%S')
    
    Path(os.path.dirname(log_path)).mkdir(parents=True, exist_ok=True)
    file_handler = TimedRotatingFileHandler(log_path, when="d")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    global __logger
    __logger.addHandler(console_handler)
    __logger.addHandler(file_handler)    
    __logger.setLevel(log_level)

    return __logger


def remove_emojis(text):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F700-\U0001F77F"  # alchemical symbols
                           u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                           u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                           u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                           u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                           u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                           u"\U00002702-\U000027B0"  # Dingbat symbols
                           u"\U000024C2-\U0001F251"  # Enclosed characters
                           "]+", flags=re.UNICODE)
    
    return emoji_pattern.sub(r'', text)
