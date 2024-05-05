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


    def subscribe(self, topic, topic_handler=None, datatype="str"):
        request_topic = f"{SUBSCRIBE_HEADER}.{topic}"
        logger.debug(f"request_topic: {request_topic}")
        self.agent.subscribe(request_topic, datatype, self.handle_request)

        if topic_handler:
            self.agent.set_topic_handler(topic, topic_handler)

    
    def deep_find_deepest(key, dictionary, depth=0):
        deepest_value = None
        max_depth = -1

        if key in dictionary:
            deepest_value = dictionary[key]
            max_depth = depth

        for subkey, subvalue in dictionary.items():
            if isinstance(subvalue, dict):  # Only search in sub-dictionaries
                found_value, found_depth = ResponseLogistic.deep_find_deepest(key, subvalue, depth + 1)
                if found_depth > max_depth:
                    deepest_value = found_value
                    max_depth = found_depth

        return deepest_value, max_depth


    def response_publish(self, topic, result, source_payload):
        sender_id = ResponseLogistic.deep_find_deepest('sender', source_payload)[0]
        request_id = ResponseLogistic.deep_find_deepest('request_id', source_payload)[0]
        logistic_topic = f"{PUBLISH_HEADER}.{sender_id}.{request_id}.{topic}"
        packed_payload = self._payload_wrapper.wrap_for_response(result, source_payload)
        logger.debug(f"logistic_topic: {logistic_topic}, packed_payload: {str(packed_payload)[:300]}..")
        self.agent.publish(logistic_topic, packed_payload)


    def response(self, topic, result, source_payload):
        sender_id = source_payload['sender']
        request_id = source_payload['request_id']
        logistic_topic = f"{PUBLISH_HEADER}.{sender_id}.{request_id}.{topic}"
        packed_payload = self._payload_wrapper.wrap_for_response(result, source_payload)
        logger.debug(f"logistic_topic: {logistic_topic}, packed_payload: {str(packed_payload)[:300]}..")
        self.agent.publish(logistic_topic, packed_payload)

        
    def handle_request(self, topic:str, payload):
        logger.debug(f"topic: {topic}, payload: {str(payload)[:300]}..")
        request_topic = topic[len(SUBSCRIBE_HEADER)+1:]
        request_payload = self._payload_wrapper.unpack(payload)
        logger.debug(f"request_payload: {str(request_payload)[:300]}")
        
        def on_message(request_topic, request_payload):
            output = self.agent._on_message(request_topic, request_payload["content"], request_payload)
            logger.debug(f"output: {str(output)[:300]}")
            if output and isinstance(output, tuple) and len(output) == 2:
                resp_topic, resp_result = output
                self.response(resp_topic, resp_result, request_payload)

        threading.Thread(target=on_message, 
                         args=(request_topic, request_payload)).start()
        # self.agent._on_message(request_topic, request_payload["content"])
