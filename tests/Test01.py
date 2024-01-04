import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import multiprocessing
from multiprocessing import Process
import signal
import threading
import time

from holon.HolonicAgent import HolonicAgent

import json
# from opencc import OpenCC

import helper
from holon.HolonicAgent import HolonicAgent

from abdi_config import AbdiConfig

logger = helper.get_logger()


class TestAgent(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def on_connected(self):
        self.subscribe("test.start")
        # self.subscribe("doc.text.import", "str", self.handle_doc_text_import)
        pass


    def handle_doc_text_import(self, topic:str, payload):
        text = payload.decode('utf-8', 'ignore')
        file_info = json.loads(text)
        file_text = file_info['text']
        logger.info(f"topic: {topic}, Prep text: {file_text.encode('utf-8')}")


    def on_message(self, topic:str, payload):
        if "test.start" == topic:
            logger.debug("Got: test.start")
            self.publish("test.send", self.wrap_head("【前進新台灣 PART2】"))


if __name__ == '__main__':
    print('***** Test start *****')

    def signal_handler(signal, frame):
        print("signal_handler")
        # exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    multiprocessing.set_start_method('spawn')

    TestAgent(AbdiConfig(helper.get_config())).start()

    print('***** Test STOP *****')
