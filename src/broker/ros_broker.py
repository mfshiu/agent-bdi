import logging

from broker.message_broker import MessageBroker
from broker.notifier import BrokerNotifier
from abdi_config import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class RosBroker(MessageBroker):
    def __init__(self, notifier:BrokerNotifier):
        logger.info(f"Initialize...")
        
        super().__init__(notifier=notifier)



    ###################################
    # Implementation of MessageBroker #
    ###################################
    
    
    def start(self, options:dict):
        logger.info(f"Ros broker is starting...")
       

    def stop(self):
        logger.info(f"Ros broker is stopping...")


    def publish(self, topic:str, payload):
        logger.info(f"topic: {topic}, payload: {payload}")
        
    
    def subscribe(self, topic:str, data_type):
        logger.info(f"topic: {topic}")
