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
    __handlers = {}
    
    
    def __init__(self, agent:HolonicAgent, request_id=""):
        self.agent = agent
        self.request_id = request_id
        self.response_topic_header = f"{SUBSCRIBE_HEADER}.{self.agent.agent_id}.{self.request_id}"
        logger.debug(f"self, agent_id: {self.agent.agent_id}, short_id: {self.agent.short_id}, request_id: {self.request_id}")
        self._payload_wrapper = PayloadWrapper(self.agent.agent_id)
        
        
    def publish(self, topic, payload):
        logistic_topic = f"{PUBLISH_HEADER}.{topic}"
        logger.debug(f"agent_id: {self.agent.agent_id}, request_id: {self.request_id}")
        packed_payload = self._payload_wrapper.wrap_for_request(payload, self.request_id)
        # logistic_topic, packed_payload = self.pack(topic, payload)
        logger.debug(f"logistic_topic: {logistic_topic}, packed_payload: {str(packed_payload)[:300]}")
        self.agent.publish(logistic_topic, packed_payload)


    def subscribe(self, topic, topic_handler=None, datatype="str"):
        response_topic = f"{self.response_topic_header}.{topic}"
        self.agent.subscribe(response_topic, datatype, self.handle_response)
        RequestLogistic.__handlers[self.response_topic_header] = topic_handler


    def handle_response(self, topic:str, payload):
        responsed_topic = topic[len(self.response_topic_header)+1:]
        unpacked = self._payload_wrapper.unpack(payload)
        logger.debug(f"topic: {topic}, unpacked: {str(unpacked)[:300]}")

        if topic_handler := RequestLogistic.__handlers[self.response_topic_header]:
            self.agent.set_topic_handler(responsed_topic, topic_handler)
        self.agent._on_message(responsed_topic, unpacked["content"])


    # def handle_response(self, topic:str, payload):
    #     responsed_topic = topic[len(self.response_topic_header)+1:]
    #     # unpacked = self.unpack(payload)
    #     unpacked = self._payload_wrapper.unpack(payload)
    #     if unpacked["receiver"] == self.agent.agent_id:
    #         if unpacked["request_id"] == self.request_id:
    #             logger.debug(f"MATCHED, agent_id: {self.agent.agent_id}, request_id: {self.request_id}")
    #             self.agent._on_message(responsed_topic, unpacked["content"])
    #         else:
    #             logger.debug(f"NOT matched, request_id: {unpacked['request_id']}, self.request_id: {self.request_id}")
    #     else:
    #         logger.debug(f"NOT matched, receiver: {unpacked['receiver']}, agent_id: {self.agent.agent_id}")
            


    # def pack(self, topic:str, payload):
    #     if topic == self.request_topic:
    #         # request_id = str(uuid.uuid4())
    #         packed = self._payload_wrapper.wrap_for_request(payload, self.request_id)
    #         # logger.debug(f"packed: {packed}")
    #         return f"{PUBLISH_HEADER}.{topic}", packed
    #     else:
    #         return topic, payload


    # def unpack(self, payload):
    #     unpacked = self._payload_wrapper.unpack(payload)
    #     return unpacked
