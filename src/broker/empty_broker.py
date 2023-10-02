from broker.message_broker import MessageBroker
from broker.notifier import BrokerNotifier
import helper


logger = helper.get_logger()


class EmptyBroker(MessageBroker):
    def __init__(self, notifier:BrokerNotifier):
        logger.info(f"Initialize...")
        
        super().__init__(notifier=notifier)



    ###################################
    # Implementation of MessageBroker #
    ###################################
    
    
    def start(self, options:dict):
        logger.info(f"Empty broker is starting. options:{options}")
       

    def stop(self):
        logger.info(f"Empty broker is stopping...")


    def publish(self, topic:str, payload):
        logger.info(f"topic: {topic}, payload: {payload}")
        
    
    def subscribe(self, topic:str):
        logger.info(f"topic: {topic}")
