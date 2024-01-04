# import atexit
import inspect
from multiprocessing import Process
import os
import signal
import sys
import threading
import time 
from typing import final

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import logging

from abdi_config import AbdiConfig, LOGGER_NAME
from broker.notifier import BrokerNotifier
from broker.broker_maker import BrokerMaker
from core.Agent import Agent
from holon.Blackboard import Blackboard
from holon.HolonicDesire import HolonicDesire
from holon.HolonicIntention import HolonicIntention


logger = logging.getLogger(LOGGER_NAME)

# def callback_with_error():
#     print("This callback will throw an error.")
#     # raise ValueError("Oops! An error occurred.")

# atexit.register(callback_with_error)


class HolonicAgent(Agent, BrokerNotifier) :
    def __init__(self, config:AbdiConfig=None, b:Blackboard=None, d:HolonicDesire=None, i: HolonicIntention=None):
        b = b or Blackboard()
        d = d or HolonicDesire()
        i = i or HolonicIntention()
        super().__init__(b, d, i)
        
        self.config = config if config else AbdiConfig(options={})
        self.head_agents = []
        self.body_agents = []
        self.__run_interval_seconds = 1
        
        self.name = f'<{self.__class__.__name__}>'
        self._agent_proc = None        
        self._broker = None
        self._topic_handlers = {}


    @final
    def start(self, head=False):
        self._agent_proc = Process(target=self._run, args=(self.config,))
        self._agent_proc.start()
        
        for a in self.head_agents:
            a.start()
        for a in self.body_agents:
            a.start()
        
        if head:
            try:
                self._agent_proc.join()
            except:
                logger.warning(f"{self.name} terminated.")



# =====================
#  Instance of Process 
# =====================


    def is_running(self):
        return not self._terminate_lock.is_set()


    def _run(self, config:AbdiConfig):
        self.config = config
        self._run_begin()
        self._running()
        self._run_end()
    

    def _run_begin(self):
        self.on_begining()

        def signal_handler(signal, frame):
            logger.warning(f"{self.name} Ctrl-C: {self.__class__.__name__}")
            self.terminate()
        signal.signal(signal.SIGINT, signal_handler)

        self._terminate_lock = threading.Event()
        
        logger.debug(f"create broker")
        if broker_type := self.config.get_broker_type():
            self._broker = BrokerMaker().create_broker(
                broker_type=broker_type, 
                notifier=self)
            self._broker.start(options=self.config.options)
        
        logger.debug(f"start interval_loop")
        def interval_loop():
            while not self._terminate_lock.is_set():
                self.on_interval()
                time.sleep(self.__run_interval_seconds)
        threading.Thread(target=interval_loop).start()
            
        self.on_began()
        
        
    def get_run_interval(self):
        return self.__run_interval_seconds
        
        
    def set_run_interval(self, seconds):
        self.__run_interval_seconds = seconds


    def on_begining(self):
        pass


    def on_began(self):
        pass


    def on_interval(self):
        pass


    def _running(self):
        self.on_running()


    def on_running(self):
        pass


    def _run_end(self):
        self.on_terminating()

        while not self._terminate_lock.is_set():
            self._terminate_lock.wait(1)
        self._broker.stop() 
        
        self.on_terminated()


    def on_terminating(self):
        pass


    def on_terminated(self):
        pass


    @final
    def publish(self, topic, payload=None):
        return self._broker.publish(topic, payload)


    # def publish(self, topic, payload=None):
    #     if payload:
    #         wapped_payload = self._payload_wrapper.wrap(payload)
    #         return self._publish(topic, wapped_payload)
    #     else:
    #         return self._publish(topic, payload)

    @final
    def subscribe(self, topic, data_type="str", topic_handler=None):
        if topic_handler:
            logger.debug(f"Add topic handler: {topic}")
            self._topic_handlers[topic] = topic_handler
        return self._broker.subscribe(topic, data_type)
        

    @final
    def terminate(self):
        logger.warn(f"{self.name}.")

        for a in self.head_agents:
            name = a.__class__.__name__
            self.publish(topic='terminate', payload=name)

        for a in self.body_agents:
            name = a.__class__.__name__
            self.publish(topic='terminate', payload=name)

        self._terminate_lock.set()



# ==================================
#  Implementation of BrokerNotifier 
# ==================================

    
    def _on_connect(self):
        logger.info(f"{self.name} Broker is connected.")
        
        self.subscribe("echo")
        self.subscribe("terminate")
        self.on_connected()
            
            
    def on_connected():
        pass


    def _on_message(self, topic:str, payload):
        if topic in self._topic_handlers:
            self._topic_handlers[topic](topic, payload)
        else:
            self.on_message(topic, payload)
            
            
    def on_message(self, topic:str, payload):
        pass



# ==================================
#  Others operation 
# ==================================


    def _convert_to_text(self, payload) -> str:
        if payload:
            data = payload.decode('utf-8', 'ignore')
        else:
            data = None
        
        return data
    
    
    def decode(self, payload):
        try:
            data = payload.decode('utf-8', 'ignore')
        except Exception as ex:
            logger.error(f"Type: {type(ex)}")
            logger.exception(ex)
            data = ""
            
        return data.strip()
        