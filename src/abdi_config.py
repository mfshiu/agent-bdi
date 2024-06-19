import logging

from broker import BrokerType


class AbdiConfig:
    LOGGER_NAME = "ABDI"
    
    def __init__(self, options=None):
        self.options = options if options else {}

        self.log_level = logging.DEBUG
        self.log_dir = "./_log"
        
        
    def get_broker_type(self) -> BrokerType:
        if broker_type := self.get("broker_type"):
            return BrokerType(broker_type.lower())
        else:
            return BrokerType.Empty
        
    
    def get(self, key:str, default=None):
        return self.options.get(key, default)
        
    
    def set(self, key:str, value):
        self.options[key] = value
