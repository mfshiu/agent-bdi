import logging

from abdi_config import AbdiConfig
from holon.HolonicAgent import HolonicAgent
from holon.logistics.base_logistic import BaseLogistic
from holon.logistics.payload_wrapper import PayloadWrapper


logger = logging.getLogger(AbdiConfig.LOGGER_NAME)
PUBLISH_HEADER = "@request"
SUBSCRIBE_HEADER = "@response"


class RequestLogistic(BaseLogistic):
    __handlers = {}
    
    
    def __init__(self, agent:HolonicAgent=None, request_id="", job_topic=None):
        self.agent = agent
        self.job_topic = job_topic
        self.request_id = request_id
        self.response_topic_header = f"{SUBSCRIBE_HEADER}.{self.agent.agent_id}.{self.request_id}"
        logger.debug(f"self, agent_id: {self.agent.agent_id}, short_id: {self.agent.short_id}, request_id: {self.request_id}")
        self._payload_wrapper = PayloadWrapper(self.agent.agent_id)
        
        
    # def publish(self, payload, source_payload=None):
    #     if not self.job_topic:
    #         raise Exception("The job topic has not been set yet.")
    #     self.publish(self.job_topic, payload, source_payload)
        
        
    def publish(self, topic, payload, source_payload=None):
        if not topic:
            if self.job_topic:
                topic = self.job_topic
            else:
                raise Exception("The job topic has not been set yet.")

        logger.debug(f"topic: {topic}, source_payload: {str(source_payload)[:300]}..")
        logistic_topic = f"{PUBLISH_HEADER}.{topic}"
        logger.debug(f"agent_id: {self.agent.agent_id}, request_id: {self.request_id}")
        packed_payload, request_token = self._payload_wrapper.wrap_for_request(payload, self.request_id, source_payload)
        logger.debug(f"logistic_topic: {logistic_topic}, packed_payload: {str(packed_payload)[:300]}..")
        self.agent.publish(logistic_topic, packed_payload)

        return request_token


    # def subscribeA(self, topic_handler=None, datatype="str"):
    #     if not self.job_topic:
    #         raise Exception("The job topic has not been set yet.")
    #     self.subscribe(self.job_topic, topic_handler, datatype)
        
        
    def subscribe(self, topic=None, topic_handler=None, datatype="str"):
        if not topic:
            if self.job_topic:
                topic = self.job_topic
            else:
                raise Exception("The job topic has not been set yet.")
        response_topic = f"{self.response_topic_header}.{topic}"
        logger.debug(f"response_topic: {response_topic}")
        RequestLogistic.__handlers[self.response_topic_header] = topic_handler
        return self.agent.subscribe(response_topic, datatype, self.handle_response)


    def handle_response(self, topic:str, payload):
        responsed_topic = topic[len(self.response_topic_header)+1:]
        unpacked = self._payload_wrapper.unpack(payload)
        logger.debug(f"topic: {topic}, unpacked: {str(unpacked)[:300]}..")

        if topic_handler := RequestLogistic.__handlers[self.response_topic_header]:
            self.agent.set_topic_handler(responsed_topic, topic_handler)
        self.agent._on_message(topic=responsed_topic, 
                               payload=unpacked["content"], 
                               source_payload=unpacked)
