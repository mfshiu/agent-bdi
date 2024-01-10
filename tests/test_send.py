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


class TestResp(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def on_connected(self):
        self.subscribe("test.send")
        
        
    def on_request(self, topic, payload):
        if "test.send" == topic:
            # req_payload = payload.decode("utf-8", "ignore")
            resp_payload = "帶您互動討論最熱政治熱題"
            return "test.resp", resp_payload


    def on_message(self, topic:str, payload):
        pass


class TestSend(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def on_connected(self):
        self.subscribe("test.start")
        self.subscribe("test.resp", data_type="str", topic_handler=self.process_resp)
        # self.subscribe("doc.text.import", "str", self.handle_doc_text_import)
        pass


    def on_message(self, topic:str, payload):
        if "test.start" == topic:
            logger.debug("Got: test.start")
            # self.request("test.send", "【前進新台灣 PART2】")
            
            
    def process_resp(self, topic, payload):
        logger.info(f"TestSend1, Agent: {self.agent_id}, topic:{topic}, payload:{payload}")


class TestSend2(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def on_connected(self):
        self.subscribe("test.start")
        self.subscribe("test.resp", data_type="str", topic_handler=self.process_resp)


    def on_message(self, topic:str, payload):
        if "test.start" == topic:
            logger.debug("Got: test.start")
            self.request("test.send", "【前進新台灣 PART2】")
            
            
    def process_resp(self, topic, payload):
        logger.info(f"TestSend2, Agent: {self.agent_id}, topic:{topic}, payload:{payload}")


if __name__ == '__main__':
    print('***** Test start *****')

    def signal_handler(signal, frame):
        print("signal_handler")
        # exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    multiprocessing.set_start_method('spawn')

    TestSend(AbdiConfig(helper.get_config())).start()
    TestSend2(AbdiConfig(helper.get_config())).start()
    TestResp(AbdiConfig(helper.get_config())).start()

    print('***** Test STOP *****')
