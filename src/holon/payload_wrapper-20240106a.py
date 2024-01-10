import json
import logging
import uuid

from abdi_config import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)
VERSION = "0001"
# WRAPPER_HEAD = "950f7f7ba7c111eea5c4ff9ca9F3fcfd"
# WRAPPER_HEAD = "950f7f7ba7c111ee"
WRAPPER_REQUEST_HEAD = "950f7f7ba7c111ee"
WRAPPER_RESPONSE_HEAD = "a5c4ff9ca9F3fcfd"
WRAPPER_REQUEST_HEAD_BYTES = WRAPPER_REQUEST_HEAD.encode("utf-8")
WRAPPER_RESPONSE_HEAD_BYTES = WRAPPER_RESPONSE_HEAD.encode("utf-8")
WRAPPER_HEAD_LENGTH = len(WRAPPER_REQUEST_HEAD)


class PayloadWrapper:
    def __init__(self, agent_id:str):
        self.agent_id = agent_id
        
        
    def is_request(self, payload:bytes):
        managed = False

        if payload and len(payload) >= WRAPPER_HEAD_LENGTH:
            head_bytes = payload[:WRAPPER_HEAD_LENGTH]
            managed = head_bytes == WRAPPER_REQUEST_HEAD

        return managed
        
        
    def is_request(self, payload:bytes):
        return self.__check_head(payload, WRAPPER_REQUEST_HEAD_BYTES)
        
        
    def is_response(self, payload:bytes):
        return self.__check_head(payload, WRAPPER_RESPONSE_HEAD_BYTES)
    
    
    def __check_head(self, payload:bytes, head_to_check):
        managed = False

        if payload:
            head_bytes = payload[:len(head_to_check)]
            managed = head_bytes == head_to_check

        return managed


    def unpack(self, payload) -> str:
        payload_text = payload.decode('utf-8')
        payload_json = json.loads(payload_text[WRAPPER_HEAD_LENGTH:])
        # logger.debug(f"payload_json: {payload_json}")
        if VERSION != payload_json["version"]:
            raise Exception("Invalid payload version.")
        return payload_json


    def wrap_for_response(self, payload, managed_request_payload:str) -> str:
        receiver_agent_id = managed_request_payload["sender"]
        resp_json = {
            "version": VERSION,
            "receiver": receiver_agent_id
        }
        resp_json["content"] = payload

        resp = f"{WRAPPER_RESPONSE_HEAD}{json.dumps(resp_json)}"
        return resp


    def wrap_for_request(self, payload) -> str:
        request_json = {
            "version": VERSION,
            "sender": self.agent_id
        }
        request_json["content"] = payload

        request_payload = f"{WRAPPER_REQUEST_HEAD}{json.dumps(request_json)}"
        return request_payload
