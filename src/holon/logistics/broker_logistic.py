import logging

from abdi_config import LOGGER_NAME
from holon.logistics.base_logistic import BaseLogistic


logger = logging.getLogger(LOGGER_NAME)



class BrokerLogistic(BaseLogistic):
    def __init__(self):
        pass


    def pack(self, payload):
        return payload


    def unpack(self, payload):
        return payload
