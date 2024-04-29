import logging
import threading

from abdi_config import LOGGER_NAME
from holon.HolonicAgent import HolonicAgent
from holon.logistics.base_logistic import BaseLogistic
from holon.logistics.payload_wrapper import PayloadWrapper


logger = logging.getLogger(LOGGER_NAME)
PUBLISH_HEADER = "@response"
SUBSCRIBE_HEADER = "@request"


class ResponseLogistic(BaseLogistic):
    def __init__(self, agent:HolonicAgent):
        self.agent = agent
        self._payload_wrapper = PayloadWrapper(self.agent.agent_id)
        
        
    # def publish(self, topic, payload):
    #     sender_id = self.request_payload['sender']
    #     request_id = self.request_payload['request_id']
    #     logistic_topic = f"{PUBLISH_HEADER}.{sender_id}.{request_id}.{topic}"
    #     packed_payload = self._payload_wrapper.wrap_for_response(payload, self.request_payload)
    #     logger.debug(f"logistic_topic: {logistic_topic}, packed_payload: {str(packed_payload)[:300]}")
    #     # logger.debug(f"logistic_topic: {logistic_topic}, packed_payload: {str(packed_payload)}")
    #     # self.agent.publish(logistic_topic, str(packed_payload))
    #     self.agent.publish(logistic_topic, packed_payload)


    def subscribe(self, topic, topic_handler=None, datatype="str"):
        request_topic = f"{SUBSCRIBE_HEADER}.{topic}"
        logger.debug(f"request_topic: {request_topic}")
        self.agent.subscribe(request_topic, datatype, self.handle_request)

        if topic_handler:
            self.agent.set_topic_handler(topic, topic_handler)

        
    def handle_request(self, topic:str, payload):
        logger.debug(f"topic: {topic}, payload: {str(payload)[:300]}...")
        request_topic = topic[len(SUBSCRIBE_HEADER)+1:]
        request_payload = self._payload_wrapper.unpack(payload)
        
        def on_message(request_topic, request_payload):
            output = self.agent._on_message(request_topic, request_payload["content"])
            if output and isinstance(output, tuple) and len(output) == 2:
                resp_topic, resp_result = output
                sender_id = request_payload['sender']
                request_id = request_payload['request_id']
                logistic_topic = f"{PUBLISH_HEADER}.{sender_id}.{request_id}.{resp_topic}"
                packed_payload = self._payload_wrapper.wrap_for_response(resp_result, request_payload)
                logger.debug(f"logistic_topic: {logistic_topic}, packed_payload: {str(packed_payload)[:300]}")
                self.agent.publish(logistic_topic, packed_payload)
            
        threading.Thread(target=on_message, 
                         args=(request_topic, request_payload)).start()
        # self.agent._on_message(request_topic, request_payload["content"])

        
    # def handle_request(self, topic:str, payload):
    #     logger.debug(f"topic: {topic}, payload: {str(payload)[:300]}...")
    #     request_topic = topic[len(SUBSCRIBE_HEADER)+1:]
    #     self.request_payload = self._payload_wrapper.unpack(payload)
    #     content = self.request_payload["content"]
    #     # logger.debug(f"request_topic: {request_topic}, agent_id: {self.agent.agent_id}, content: {content}")
    #     self.agent._on_message(request_topic, content)
