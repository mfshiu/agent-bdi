from abc import ABC, abstractmethod


class BrokerNotifier(ABC):
        
    def __init__(self):
        pass
        
    
    @abstractmethod
    def _on_connect(self):        
        """Called when connected to the broker."""
        
    
    @abstractmethod
    def _on_message(self, message):        
        """Called when a message comes in."""
        
    
    @abstractmethod
    def _on_topic(self, topic, data):        
        """Called when a subscribed topic comes in."""
