# import atexit
import inspect
from multiprocessing import Process
import os
import signal
import sys
import threading
import time 
from typing import final
import uuid

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
from holon.payload_wrapper import PayloadWrapper
from holon.payload import Payload


logger = logging.getLogger(LOGGER_NAME)



class HolonicAgent(Agent, BrokerNotifier) :
    def __init__(self, config:AbdiConfig=None, b:Blackboard=None, d:HolonicDesire=None, i: HolonicIntention=None):
        b = b or Blackboard()
        d = d or HolonicDesire()
        i = i or HolonicIntention()
        super().__init__(b, d, i)
        
        self.agent_id = None
        self.config = config if config else AbdiConfig(options={})
        self.head_agents = []
        self.body_agents = []
        self.__run_interval_seconds = 1
        
        self.name = f'<{self.__class__.__name__}>'
        self._agent_proc = None        
        self._broker = None
        self._topic_handlers = {}
        self._payload_wrapper = None


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

    
    def unpack(self, payload):
        if self._payload_wrapper.is_managed(payload):
            return self._payload_wrapper.unpack(payload)
        else:
            return payload


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

        self.agent_id = str(uuid.uuid1()).replace("-", "")
        self._terminate_lock = threading.Event()
        self._payload_wrapper = PayloadWrapper(self.agent_id)
        
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
        
        
    @final
    def request(self, topic, payload):
        logger.debug(f"payload: {len(payload)}")
        wrapped = self._payload_wrapper.wrap_for_request(payload)
        # logger.debug(f"wrapped: {len(wrapped)}")
        self.publish(topic, wrapped)
        
    
    def _on_response(self, topic, payload):
        managed_payload = self._payload_wrapper.unpack(payload)
        logger.debug(f"receiver: {managed_payload['receiver']}, agent_id: {self.agent_id}")
        if managed_payload["receiver"] == self.agent_id:
            self._on_message(topic, managed_payload["content"])


    def on_request(self, topic, payload):
        raise NotImplementedError()
        
    
    def _on_request(self, topic, payload):
        managed_payload = self._payload_wrapper.unpack(payload)

        handler = self._topic_handlers[topic] if topic in self._topic_handlers else self.on_request
        response_topic, response_payload = handler(topic, managed_payload["content"])
        logger.debug(f"response_topic: {response_topic}")
        if not response_payload:
            logger.warning(f"response_payload is None or empty.")
        
        if response_topic:
            managed_payload = self._payload_wrapper.wrap_for_response(response_payload, managed_payload)
            # logger.debug(f"response_payload: {response_payload}, managed_payload: {managed_payload}")
            self.publish(response_topic, managed_payload)
        

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
            
            
    def on_connected(self):
        pass


    def _on_message(self, topic:str, payload):
        self._process_message(topic, payload)
        
        
    @final
    def _process_message(self, topic:str, payload):
        logger.debug(f"payload: {len(payload)}")
        if payload and self._payload_wrapper.is_request(payload):
            logger.debug("message is_request")
            self._on_request(topic, payload)
        elif payload and self._payload_wrapper.is_response(payload):
            logger.debug(f"message is_response")
            self._on_response(topic, payload)
        else:
            logger.debug(f"unmanaged payload")
            if topic in self._topic_handlers:
                self._topic_handlers[topic](topic, payload)
            else:
                self.on_message(topic, payload)


    def on_message(self, topic:str, payload:Payload):
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
        