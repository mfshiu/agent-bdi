import logging
import uuid

from abdi_config import LOGGER_NAME
from holon.HolonicAgent import HolonicAgent
from holon.logistics.base_logistic import BaseLogistic
from holon.logistics.payload_wrapper import PayloadWrapper


logger = logging.getLogger(LOGGER_NAME)
PUBLISH_HEADER = "@response"
SUBSCRIBE_HEADER = "@request"


class ResponseLogistic(BaseLogistic):
    def __init__(self, agent:HolonicAgent, request_topic, request_handler=None, datatype="str"):
        self.agent = agent
        self.request_topic = request_topic

        pre_request_topic = f"{SUBSCRIBE_HEADER}.{request_topic}"
        logger.debug(f"pre_request_topic: {pre_request_topic}")
        self.agent.subscribe(pre_request_topic, datatype, self.handle_pre_request)        
        self._payload_wrapper = PayloadWrapper(self.agent.agent_id)
        
        if request_handler:
            self.agent.set_topic_handler(request_topic, request_handler)

        
    def handle_pre_request(self, topic:str, payload):
        logger.debug(f"topic: {topic}, payload: {payload}")
        request_topic = topic[len(SUBSCRIBE_HEADER)+1:]
        self.request_payload = self.unpack(payload)
        content = self.request_payload["content"]
        # logger.debug(f"request_topic: {request_topic}, agent_id: {self.agent.agent_id}, content: {content}")
        self.agent._on_message(request_topic, content)


    def pack(self, topic:str, payload):
        if topic == self.request_topic:
            packed = self._payload_wrapper.wrap_for_response(payload, self.request_payload)
            return f"{PUBLISH_HEADER}.{topic}", packed
        else:
            return topic, payload


    def unpack(self, payload):
        unpacked = self._payload_wrapper.unpack(payload)
        return unpacked
