import json
import logging
from queue import Queue
import random
import threading
import time

from abdi_config import LOGGER_NAME
from holon.HolonicAgent import HolonicAgent
from holon.logistics.base_logistic import BaseLogistic


logger = logging.getLogger(LOGGER_NAME)
HEADER_RANKING = "@ranking"
HEADER_ELECTED = "@elected"


class LoadingCoordinator(BaseLogistic):
    def __init__(self, agent:HolonicAgent, loading_evaluator, datatype="str"):
        self.agent = agent
        self.topic_handler = None
        self.loading_evaluator = loading_evaluator
        self.loading_rate = 0
        self.candidates = None
        self.electing = False
        self.topic_payloads = Queue()

        
    def publish(self, topic, payload):
        self.agent.publish(topic, payload)


    def subscribe(self, topic, topic_handler=None, datatype="str"):
        self.topic_handler = topic_handler
        self.agent.subscribe(topic, datatype, self.start)
        self.agent.subscribe(f"{HEADER_RANKING}.{topic}", datatype, self.rank)
        self.agent.subscribe(f"{HEADER_ELECTED}.{topic}", datatype, self.elected)
        
        
    def reset(self):
        self._set_electing(False)
        self.candidates = []
        self.determine_delay = ThreadSafeCounter()
        
        
    def _set_electing(self, is_electing):
        self.electing = is_electing
        logger.debug(f"{self.agent.short_id}> set electing to {self.electing}")
        
        
    def start(self, topic:str, payload):
        logger.debug(f"{self.agent.short_id}> topic: {topic}, payload: {payload}")
        if self.electing:
            logger.warning(f"{self.agent.short_id}> electing")
            self.topic_payloads.put((topic, payload))
            return
        self.reset()
        self._set_electing(True)
        
        self.loading_rate = self.loading_evaluator(topic, payload)
        self.rank_number = self.loading_rate * 10000 + random.randint(0, 9999)
        logger.debug(f"loading_rate: {self.loading_rate}, rank_number: {self.rank_number}")

        rank_payload = {
            "agent_id": self.agent.agent_id,
            "rank_number": self.rank_number
        }
        self.candidates.append(rank_payload)
        self.agent.publish(f"{HEADER_RANKING}.{topic}", json.dumps(rank_payload))
        
        threading.Timer(.1, self.determine, args=(topic, payload)).start()


    def rank(self, topic:str, payload):
        if not self.electing:
            logger.warning(f"{self.agent.short_id}> NOT electing")
            return
            
        rank_payload = json.loads(payload.decode())
        if rank_payload['agent_id'] != self.agent.agent_id:
            self.candidates.append(rank_payload)
            
        self.determine_delay.add(0.01)
        
        
    def determine(self, topic:str, payload):
        if not self.electing:
            logger.warning(f"{self.agent.short_id}> NOT electing")
            return
        
        determine_delay = self.determine_delay.get_value()
        while determine_delay > 0:
            self.determine_delay.substract(determine_delay)
            time.sleep(determine_delay)
            determine_delay = self.determine_delay.get_value()
        
        logger.debug(f"{self.agent.short_id}> Candidates: {self.candidates}")
        # logger.debug(f"{self.agent.short_id}> candidates size: {len(self.candidates)}")
        if len(self.candidates):
            min_agent = min(self.candidates, key=lambda x: (x['rank_number'], x['agent_id']))
            if self.agent.agent_id == min_agent['agent_id']:
                logger.info(f"{self.agent.short_id}> Elected for topic: {topic}, payload: {payload}")
                self.agent.publish(f"{HEADER_ELECTED}.{topic}", self.agent.agent_id)

                if self.topic_handler:
                    self.topic_handler(topic, payload)
                else:
                    self.agent.on_message(topic, payload)
        
        
    def elected(self, topic:str, payload):
        self.reset()
        
        elected_agent_id = payload.decode()
        if not self.topic_payloads.empty():
            work = self.topic_payloads.get()
            if self.agent.agent_id == elected_agent_id:
                next_topic, next_payload = work
                logger.info(f"{self.agent.short_id}> Next work, topic: {next_topic}, payload: {next_payload}")
                self.agent.publish(next_topic, next_payload)
            # self.start(topic=work[0], payload=work[1])


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