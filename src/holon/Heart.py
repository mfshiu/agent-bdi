from multiprocessing import Process
import paho.mqtt.client as mqtt
from holon.HolonicAgent import HolonicAgent

class Heart(HolonicAgent) :

    def __init__(self):
        super().__init__()

    # def _run(self):
    #     print(f"  run: {self.__class__.__name__}")
    #     HolonicAgent._terminate_lock.wait()
    #     print(f"  terminate: {self.__class__.__name__}")
        
    # def start(self):
    #     pass
        