import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import multiprocessing
import random
import signal
import time

import helper
from holon.HolonicAgent import HolonicAgent
from holon.logistics.loading_coordinator import LoadingCoordinator

from abdi_config import AbdiConfig

logger = helper.get_logger()


class TestLB(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def on_connected(self):
        logger.info(f"on_connected.")
        self.append_logistic(LoadingCoordinator(
            self,
            work_topic="test.work",
            work_handler=self.do_work,
            loading_evaluator=self.evaluate_loading))
        # self.subscribe("test.work", topic_handler=self.do_work)
        self.publish("test.work1")
        
        
    def evaluate_loading(self, topic, payload):
        loading_rate = random.randint(0, 100)
        # logger.info(f"loading_rate: {loading_rate}")
        
        return loading_rate
        

    def do_work(self, topic:str, payload):
        logger.info(f"{self.agent_id}({self.short_id})> Do work.")
        # time.sleep(.1)
        # logger.info(f"{self.agent_id}({self.short_id})> Do work done.")
        
        
class TestLB2(TestLB):
    def evaluate_loading(self, topic, payload):
        time.sleep(1.5)
        return super().evaluate_loading(topic, payload)


if __name__ == '__main__':
    print('***** Test loading balance *****')

    def signal_handler(signal, frame):
        print("signal_handler")
    signal.signal(signal.SIGINT, signal_handler)

    multiprocessing.set_start_method('spawn')

    for _ in range(32):
        TestLB(AbdiConfig(helper.get_config())).start()
    # TestLB2(AbdiConfig(helper.get_config())).start()
