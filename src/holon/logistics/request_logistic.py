import logging
import uuid

from abdi_config import LOGGER_NAME
from holon.HolonicAgent import HolonicAgent
from holon.logistics.base_logistic import BaseLogistic
from holon.logistics.payload_wrapper import PayloadWrapper


logger = logging.getLogger(LOGGER_NAME)
PUBLISH_HEADER = "@request"
SUBSCRIBE_HEADER = "@response"


class RequestLogistic(BaseLogistic):
    def __init__(self, agent:HolonicAgent, 
                 request_topic:str, response_handler=None, 
                 request_id="", datatype="str"):
        self.agent = agent
        self.request_topic = request_topic
        self.request_id = request_id
        
        response_topic = f"{SUBSCRIBE_HEADER}.{request_topic}"
        self.agent.subscribe(response_topic, datatype, self.handle_response)        
        self._payload_wrapper = PayloadWrapper(self.agent.agent_id)
        
        if response_handler:
            self.agent.set_topic_handler(request_topic, response_handler)
        
        
    def handle_response(self, topic:str, payload):
        responsed_topic = topic[len(SUBSCRIBE_HEADER)+1:]
        unpacked = self.unpack(payload)
        logger.debug(f"receiver: {unpacked['receiver']}, agent_id: {self.agent.agent_id}")
        if unpacked["receiver"] == self.agent.agent_id:
            if unpacked["request_id"] == self.request_id:
                self.agent._on_message(responsed_topic, unpacked["content"])


    def pack(self, topic:str, payload):
        if topic == self.request_topic:
            # request_id = str(uuid.uuid4())
            packed = self._payload_wrapper.wrap_for_request(payload, self.request_id)
            # logger.debug(f"packed: {packed}")
            return f"{PUBLISH_HEADER}.{topic}", packed
        else:
            return topic, payload


    def unpack(self, payload):
        unpacked = self._payload_wrapper.unpack(payload)
        return unpacked
