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
    def __init__(self, agent:HolonicAgent, job_topic=None):
        self.agent = agent
        self.job_topic = job_topic
        self._payload_wrapper = PayloadWrapper(self.agent.agent_id)


    # def subscribe(self, topic_handler=None, datatype="str"):
    #     if not self.job_topic:
    #         raise Exception("The job topic has not been set yet.")
    #     self.subscribe(self.job_topic, topic_handler, datatype)
        
        
    def subscribe(self, topic, topic_handler=None, datatype="str"):
        if not topic:
            if self.job_topic:
                topic = self.job_topic
            else:
                raise Exception("The job topic has not been set yet.")

        request_topic = f"{SUBSCRIBE_HEADER}.{topic}"
        logger.debug(f"request_topic: {request_topic}")
        self.agent.subscribe(request_topic, datatype, self.handle_request)

        if topic_handler:
            self.agent.set_topic_handler(topic, topic_handler)
            
            
    def get_original_topic(self, source_payload):
        topic = ResponseLogistic._deep_find_deepest('request_topic', source_payload)
        return topic[0] if topic else None

    
    def _deep_find_deepest(key, dictionary, depth=0):
        deepest_value = None
        max_depth = -1

        if key in dictionary:
            deepest_value = dictionary[key]
            max_depth = depth

        for subkey, subvalue in dictionary.items():
            if isinstance(subvalue, dict):  # Only search in sub-dictionaries
                found_value, found_depth = ResponseLogistic._deep_find_deepest(key, subvalue, depth + 1)
                if found_depth > max_depth:
                    deepest_value = found_value
                    max_depth = found_depth

        return deepest_value, max_depth


    def publish(self, topic=None, result=None, source_payload=None):
        if not topic:
            if self.job_topic:
                topic = self.job_topic
            else:
                raise Exception("The job topic has not been set yet.")

        sender_id = ResponseLogistic._deep_find_deepest('sender', source_payload)[0]
        request_id = ResponseLogistic._deep_find_deepest('request_id', source_payload)[0]
        self.__response(topic, result, sender_id, request_id, source_payload)
        # logistic_topic = f"{PUBLISH_HEADER}.{sender_id}.{request_id}.{topic}"
        # packed_payload = self._payload_wrapper.wrap_for_response(result, source_payload)
        # logger.debug(f"logistic_topic: {logistic_topic}, packed_payload: {str(packed_payload)[:300]}..")
        # self.agent.publish(logistic_topic, packed_payload)


    def _response(self, topic, result, source_payload):
        sender_id = source_payload['sender']
        request_id = source_payload['request_id']
        self.__response(topic, result, sender_id, request_id, source_payload)
        # logistic_topic = f"{PUBLISH_HEADER}.{sender_id}.{request_id}.{topic}"
        # packed_payload = self._payload_wrapper.wrap_for_response(result, source_payload)
        # logger.debug(f"logistic_topic: {logistic_topic}, packed_payload: {str(packed_payload)[:300]}..")
        # self.agent.publish(logistic_topic, packed_payload)


    def __response(self, topic, result, sender_id, request_id, source_payload):
        logistic_topic = f"{PUBLISH_HEADER}.{sender_id}.{request_id}.{topic}"
        packed_payload = self._payload_wrapper.wrap_for_response(result, source_payload)
        logger.debug(f"logistic_topic: {logistic_topic}, packed_payload: {str(packed_payload)[:300]}..")
        self.agent.publish(logistic_topic, packed_payload)

        
    def handle_request(self, topic:str, payload):
        logger.debug(f"topic: {topic}, payload: {str(payload)[:300]}..")
        request_topic = topic[len(SUBSCRIBE_HEADER)+1:]
        request_payload = self._payload_wrapper.unpack(payload)
        request_payload['request_topic'] = request_topic
        logger.debug(f"request_payload: {str(request_payload)[:300]}..")
        
        def on_message(request_topic, request_payload):
            output = self.agent._on_message(request_topic, request_payload["content"], request_payload)
            logger.debug(f"output: {str(output)[:300]}..")
            if output and isinstance(output, tuple) and len(output) == 2:
                resp_topic, resp_result = output
                self._response(resp_topic, resp_result, request_payload)

        threading.Thread(target=on_message, 
                         args=(request_topic, request_payload)).start()
        # self.agent._on_message(request_topic, request_payload["content"])
