import copy
import json
import logging
import pickle
import uuid

from abdi_config import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)
VERSION = "0001"
VERSION_BYTES = VERSION.encode('utf-8')
# WRAPPER_HEAD = "950f7f7ba7c111eea5c4ff9ca9F3fcfd"
# WRAPPER_HEAD = "950f7f7ba7c111ee"
WRAPPER_REQUEST_HEAD = "950f7f7ba7c111ee"
WRAPPER_RESPONSE_HEAD = "a5c4ff9ca9F3fcfd"
WRAPPER_REQUEST_HEAD_BYTES = WRAPPER_REQUEST_HEAD.encode("utf-8")
WRAPPER_RESPONSE_HEAD_BYTES = WRAPPER_RESPONSE_HEAD.encode("utf-8")


class PayloadWrapper:
    def __init__(self, agent_id:str):
        self.binary_wrapper = BinaryWrapper(self)
        self.text_wrapper = TextWrapper(self)
        self.agent_id = agent_id
        
        
    def create_response_json(self, response_payload, request_payload):
        response_json = copy.deepcopy(request_payload)
        # response_json = {
        #     "version": VERSION,
        #     "request_id": request_payload["request_id"],
        #     "receiver": request_payload["sender"],
        #     "request_token": request_payload["request_token"]
        # }
        response_json["version"] = VERSION
        response_json["content"] = response_payload

        # if 'source_payload' in request_payload:
        #     response_json["source_payload"] = request_payload["source_payload"]
        
        return response_json
        
        
    def create_request_json(self, payload, request_id, source_payload):
        request_json = {
            "version": VERSION,
            "request_id": request_id,
            "sender": self.agent_id,
            "request_token": str(uuid.uuid4()).replace("-", "")
        }
        request_json["content"] = payload

        if source_payload:
            request_json["source_payload"] = source_payload
        
        return request_json
        

    def get_payload_wrapper(self, payload):
        # logger.debug(f"get_payload_wrapper, payload: {payload}, type: {type(payload)}")
        if payload:
            if self.text_wrapper.is_acceptable(payload):
                return self.text_wrapper
            elif self.binary_wrapper.is_acceptable(payload):
                return self.binary_wrapper
            else:
                return None
        else:
            return payload
        
        
    def is_request(self, payload:bytes):
        return self.__check_head(payload, WRAPPER_REQUEST_HEAD_BYTES)
        
        
    def is_response(self, payload:bytes):
        return self.__check_head(payload, WRAPPER_RESPONSE_HEAD_BYTES)
    
    
    def __check_head(self, payload:bytes, head_to_check):
        managed = False

        if payload:
            head_bytes = payload[:len(head_to_check)]
            # logger.debug(f"head_bytes: {head_bytes}, head_to_check: {head_to_check}")
            managed = head_bytes == head_to_check

        return managed


    def unpack(self, payload):
        wrapper = self.get_payload_wrapper(payload)
        if wrapper:
            unpacked = wrapper.unpack(payload)
        else:
            raise Exception("Not managed payload.")
            
        return unpacked


    def wrap_for_response(self, payload:str, managed_request_payload:str) -> str:
        wrapper = self.get_payload_wrapper(payload)
        if wrapper:
            payload_resp = wrapper.wrap_for_response(payload, managed_request_payload)
        else:
            raise Exception(f"Unsupported payload type: {type(payload)}")

        return payload_resp


    def wrap_for_request(self, payload, request_id, source_payload) -> str:
        if wrapper := self.get_payload_wrapper(payload):
            payload_request, request_token = wrapper.wrap_for_request(payload, request_id, source_payload)
        else:
            raise Exception("Unsupported payload type.")

        return payload_request, request_token



class BinaryWrapper:
    def __init__(self, payload_wrapper:PayloadWrapper):
        self.payload_wrapper = payload_wrapper
        
        
    def is_acceptable(self, payload):
        return isinstance(payload, bytes) or isinstance(payload, bytearray)

        
    def unpack(self, payload:bytes):
        payload_body = payload[len(WRAPPER_REQUEST_HEAD_BYTES):]
        payload_json = pickle.loads(payload_body)

        if VERSION != payload_json["version"]:
            raise Exception("Invalid payload version.")

        return payload_json


    def wrap_for_request(self, payload, request_id, source_payload) -> bytes:
        request_json = self.payload_wrapper.create_request_json(payload, request_id, source_payload)
        request_payload = WRAPPER_REQUEST_HEAD_BYTES + pickle.dumps(request_json)
        
        return request_payload, request_json['request_token']
     
        
    def wrap_for_response(self, response_payload:bytes, managed_request_payload) -> bytes:
        response_json = self.payload_wrapper.create_response_json(response_payload, managed_request_payload)
        response_payload = WRAPPER_RESPONSE_HEAD_BYTES + pickle.dumps(response_json)
        
        return response_payload


            
class TextWrapper:
    def __init__(self, payload_wrapper:PayloadWrapper):
        self.payload_wrapper = payload_wrapper
        
        
    def is_acceptable(self, payload):
        if isinstance(payload, str):
            acceptable = True
        else:
            try:
                _ = payload.decode('utf-8')
                acceptable = True
            except UnicodeDecodeError:
                acceptable = False
            
        return acceptable

        
    def unpack(self, payload:str):
        payload_text = payload.decode('utf-8')
        payload_json = json.loads(payload_text[len(WRAPPER_REQUEST_HEAD):])
        logger.debug(f"payload_json: {str(payload_json)[:300]}...")
        if VERSION != payload_json["version"]:
            raise Exception("Invalid payload version.")
        return payload_json


    def wrap_for_request(self, payload, request_id, source_payload) -> str:
        request_json = self.payload_wrapper.create_request_json(payload, request_id, source_payload)
        request_payload = f"{WRAPPER_REQUEST_HEAD}{json.dumps(request_json)}"
        
        return request_payload, request_json['request_token']
                
        
    def wrap_for_response(self, response_payload:str, managed_request_payload) -> str:
        response_json = self.payload_wrapper.create_response_json(response_payload, managed_request_payload)
        response_payload = f"{WRAPPER_RESPONSE_HEAD}{json.dumps(response_json)}"
        
        return response_payload
