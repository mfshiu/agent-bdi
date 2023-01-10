from abc import ABC, abstractmethod
from core import Belief 
from core import Desire 
from core import Intention 

class Agent(ABC):
    def __init__(self, b:Belief, d:Desire, i:Intention):
        self.B = b
        self.D = d
        self.I = i

    @abstractmethod
    def start(self):
        pass