import json
import logging
import random
import threading
import time

from abdi_config import LOGGER_NAME
from holon.HolonicAgent import HolonicAgent
from holon.logistics.base_logistic import BaseLogistic
from holon.logistics.payload_wrapper import PayloadWrapper


logger = logging.getLogger(LOGGER_NAME)
HEADER_RANKING = "@ranking"
HEADER_ELECTED = "@elected"


class LoadingCoordinator(BaseLogistic):
    def __init__(self, agent:HolonicAgent, work_topic, work_handler, loading_evaluator, datatype="str"):
        self.agent = agent
        self.work_handler = work_handler
        self.loading_evaluator = loading_evaluator
        self.loading_rate = 0
        self.candidates = None
        self.electing = False
        
        self.agent.subscribe(work_topic, datatype, self.start)
        self.agent.subscribe(f"{HEADER_RANKING}.{work_topic}", datatype, self.rank)
        self.agent.subscribe(f"{HEADER_ELECTED}.{work_topic}", datatype, self.elected)
        
        
    def reset(self):
        self.candidates = []
        self.determine_delay = ThreadSafeCounter()
        
        
    def start(self, topic:str, payload):
        if self.electing:
            logger.warning(f"electing")
            return
        self.electing = True            
        self.reset()
        
        self.loading_rate = self.loading_evaluator(topic, payload)
        self.rank_number = self.loading_rate * 100 + random.randint(1, 1000000)

        rank_payload = {
            "agent_id": self.agent.agent_id,
            "rank_number": self.rank_number
        }
        self.candidates.append(rank_payload)
        self.agent.publish(f"{HEADER_RANKING}.{topic}", json.dumps(rank_payload))
        
        threading.Timer(.1, self.determine, args=(topic, payload)).start()


    def rank(self, topic:str, payload):
        if not self.electing:
            logger.warning(f"NOT electing")
            return
            
        rank_payload = json.loads(payload.decode())
        if rank_payload['agent_id'] != self.agent.agent_id:
            self.candidates.append(rank_payload)
            
        self.determine_delay.add(0.01)
        
        
    def determine(self, topic:str, payload):
        if not self.electing:
            logger.warning(f"NOT electing")
            return
        
        determine_delay = self.determine_delay.get_value()
        while determine_delay > 0:
            self.determine_delay.substract(determine_delay)
            time.sleep(determine_delay)
            determine_delay = self.determine_delay.get_value()
        
        # logger.debug(f"candidates: {self.candidates}")
        logger.debug(f"{self.agent.short_id}> candidates size: {len(self.candidates)}")
        min_agent = min(self.candidates, key=lambda x: (x['rank_number'], x['agent_id']))
        if self.agent.agent_id == min_agent['agent_id']:
            self.agent.publish(f"{HEADER_ELECTED}.{topic}", self.agent.agent_id)
            
            if self.work_handler:
                self.work_handler(topic, payload)
            else:
                self.agent.on_message(topic, payload)
        
        
    def elected(self, topic:str, payload):
        self.electing = False
        # logger.info(f"Elected agent: {payload.decode()}")


    def pack(self, topic:str, payload):
        return topic, payload


    def unpack(self, payload):
        return payload
            
            
            
class ThreadSafeCounter:
    def __init__(self, initial=0):
        self.value = initial
        self.lock = threading.Lock()
    
    def add(self, number):
        with self.lock:
            self.value += number
    
    def substract(self, number):
        with self.lock:
            self.value -= number
    
    def increment(self):
        with self.lock:
            self.value += 1
    
    def decrement(self):
        with self.lock:
            self.value -= 1
    
    def get_value(self):
        with self.lock:
            return self.value