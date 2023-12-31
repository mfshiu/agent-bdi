WRAPPER_HEAD = "950f7f7ba7c111eea5c4ff9ca9F3fcfd"
WRAPPER_HEAD_LENGTH = len(WRAPPER_HEAD)


class PayloadWrapper:
    def __init__(self, agent_uuid:str):
        self.agent_uuid = agent_uuid
        self.binary_wrapper = BinaryWrapper(self.agent_uuid)
        self.text_wrapper = TextWrapper(self.agent_uuid)
        
        
    def wrap(self, payload):
        if payload:
            if isinstance(payload, str):
                return self.text_wrapper.wrap(payload)
            elif isinstance(payload, bytes) or isinstance(payload, bytearray):
                return self.binary_wrapper.wrap(payload)
            else:
                return payload
        else:
            return payload
        
        

class BinaryWrapper:
    def __init__(self, agent_uuid:str):
        self.agent_uuid = agent_uuid.encode('ascii')        
        
        
    def wrap(self, payload):
        pass
        
            
class TextWrapper:
    def __init__(self, agent_uuid:str) -> str:
        self.agent_uuid = agent_uuid
        
        
    def unpack(self, payload):
        if payload.startswith(WRAPPER_HEAD):
                
        
    def wrap(self, payload) -> str:
        return f"{WRAPPER_HEAD}{self.agent_uuid}{payload}"
