import logging
import random
import uuid

from abdi_config import LOGGER_NAME
from holon.HolonicAgent import HolonicAgent
from holon.logistics.base_logistic import BaseLogistic
from holon.logistics.payload_wrapper import PayloadWrapper


logger = logging.getLogger(LOGGER_NAME)
DECISION_HEADER = "@decision"


class LoadingCoordinator(BaseLogistic):
    def __init__(self, agent:HolonicAgent, work_topic, work_handler, loading_evaluator, datatype="str"):
        self.agent = agent
        # self.work_topic = work_topic
        self.work_handler = work_handler
        self.loading_evaluator = loading_evaluator
        self.loading_rate = 0
        self.secondary_priority = random.randint(1, 100000000)
        self.decision_topic = f"@decision.{work_topic}"
        
        self.agent.subscribe(work_topic, datatype, self.begin_coordination)
        self.agent.subscribe(self.decision_topic, datatype, self.make_decision)
        
        
    def begin_coordination(self, topic:str, payload):
        self.loading_rate = self.loading_evaluator(topic, payload)
        self.agent.publish(self.decision_topic, )


    def make_decision(self, topic:str, payload):
        if topic == self.request_topic:
            request_id = str(uuid.uuid4())
            packed = self._payload_wrapper.wrap_for_request(payload, request_id)
            # logger.debug(f"packed: {packed}")
            return f"{PUBLISH_HEADER}.{topic}", packed
        else:
            return topic, payload
        