import inspect
import json
import logging
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

from abdi_config import AbdiConfig, LOGGER_NAME
from broker.notifier import BrokerNotifier
from broker.broker_maker import BrokerMaker
from core.Agent import Agent
from holon.Blackboard import Blackboard
from holon.HolonicDesire import HolonicDesire
from holon.HolonicIntention import HolonicIntention
from holon.logistics.base_logistic import BaseLogistic


logger = logging.getLogger(LOGGER_NAME)


class HolonicAgent(Agent, BrokerNotifier):
    def __init__(self, config:AbdiConfig=None, b:Blackboard=None, d:HolonicDesire=None, i: HolonicIntention=None):
        b = b or Blackboard()
        d = d or HolonicDesire()
        i = i or HolonicIntention()
        super().__init__(b, d, i)
        
        # self.agent_id = None
        # self.short_id = None
        self.agent_id = str(uuid.uuid4()).replace("-", "")
        self.short_id = self.agent_id[:4] #hashlib.md5(self.agent_id.encode()).hexdigest()[:6]
        self.config = config if config else AbdiConfig(options={})
        self.head_agents = []
        self.body_agents = []
        self.__run_interval_seconds = 1
        
        self.name = f'<{self.__class__.__name__}>'
        self._agent_proc = None        
        self._agent_thread = None        
        self._broker = None
        self._topic_handlers = {}
        self._echo_handlers = {}
        self.subscribed_topics = set()
        self.logistics = {}
        
        
    @final
    def register_logistic(self, logistic:BaseLogistic):
        if not logistic.job_topic:
            raise Exception("Logistic must define the job topic.")
        self.logistics[logistic.job_topic] = logistic


    @final
    def get_data(self, key:str):
        return self.__repository.get(key)


    @final
    def pop_data(self, key:str):
        data = None
        self.__repository_lock.acquire()
        if key in self.__repository:
            data = self.__repository.pop(key)
        self.__repository_lock.release()
        return data


    @final
    def put_data(self, key:str, data):
        self.__repository_lock.acquire()
        self.__repository[key] = data
        self.__repository_lock.release()        


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
                logger.warning(f"{self.short_id}> {self.name} terminated.")


    @final
    def start_thread(self, head=False):
        self._agent_thread = threading.Thread(target=self._run, args=(self.config,))
        self._agent_thread.start()
        
        for a in self.head_agents:
            a.start()
        for a in self.body_agents:
            a.start()
        
        if head:
            try:
                self._agent_thread.join()
            except:
                logger.warning(f"{self.short_id}> {self.name} terminated.")


# =====================
#  Instance of Process 
# =====================
        
        
    # def append_logistic(self, logistic:BaseLogistic):
    #     self._logistics.append(logistic)
    #     return self._logistics


    def is_running(self):
        return not self._terminate_lock.is_set()


    def _run(self, config:AbdiConfig):
        self.config = config
        self._run_begin()
        self._running()
        self._run_end()
    

    def _run_begin(self):
        self.on_begining()

        self.__repository = {}
        self.__repository_lock = threading.Lock()

        def signal_handler(signal, frame):
            logger.warning(f"{self.short_id}> {self.name} Ctrl-C: {self.__class__.__name__}")
            self.terminate()
        if self._agent_proc:
            signal.signal(signal.SIGINT, signal_handler)

        self._terminate_lock = threading.Event()
        
        logger.debug(f"{self.short_id}> Create broker")
        if broker_type := self.config.get_broker_type():
            self._broker = BrokerMaker().create_broker(
                broker_type=broker_type, 
                notifier=self)
            self._broker.start(options=self.config.options)
        
        logger.debug(f"{self.short_id}> start interval_loop")
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
    
    
    # def get_logistic(self, topic:str):
    #     if topic.startswith("@request."):
    #         return RequestLogistic(self)
    #     else:
    #         return BrokerLogistic(self)


    @final
    def publish(self, topic, payload=None):
        # logger.debug(f"topic: {topic}, payload: {payload}")
        if topic in self.logistics:
            self.logistics[topic].publish(topic, payload)
        return self._broker.publish(topic, payload)


    @final
    def _publish(self, topic, payload=None):
        return self._broker.publish(topic, payload)
        
        
    # @final
    # def request(self, topic, payload):
    #     # wrapped = self._request_logistic.pack(payload)
    #     # self.publish(topic, wrapped)
    #     self.publish(f"@request.{topic}", payload)
        
    
    def _on_response(self, topic, payload):
        managed_payload = self._request_logistic.unpack(payload)
        logger.debug(f"{self.short_id}> receiver: {managed_payload['receiver']}, agent_id: {self.agent_id}")
        if managed_payload["receiver"] == self.agent_id:
            self._on_message(topic, managed_payload["content"])


    def on_request(self, topic, payload):
        raise NotImplementedError()
        
    
    def _on_request(self, topic, payload):
        logger.debug(f"{self.short_id}> topic: {topic}, payload: {payload}")
        request_payload = self._request_logistic.unpack(payload)

        handler = self._topic_handlers[topic] if topic in self._topic_handlers else self.on_request
        response_topic, response_payload = handler(topic, request_payload["content"])
        logger.debug(f"{self.short_id}> response_topic: {response_topic}")
        if not response_payload:
            logger.warning(f"{self.short_id}> response_payload is None or empty.")
        
        if response_topic:
            response_payload = self._request_logistic.pack_for_response(response_payload, request_payload)
            # logger.debug(f"response_payload: {response_payload}, managed_payload: {managed_payload}")
            self.publish(response_topic, response_payload)
        

    @final
    def subscribe(self, topic, data_type="str", topic_handler=None):
        logger.debug(f"topic: {topic}, topic_handler: {topic_handler}")
        self.subscribed_topics.add(topic)
        
        if topic in self.logistics:
            return self.logistics[topic].subscribe(topic, topic_handler, data_type)
        else:
            if topic_handler:
                self.set_topic_handler(topic, topic_handler)
            return self._broker.subscribe(topic, data_type)
    
    
    def set_topic_handler(self, topic, handler):
        logger.debug(f"{self.short_id}> Set topic handler: {topic}")
        self._topic_handlers[topic] = handler
        

    @final
    def terminate(self, topic=None, payload=None, source_payload=None):
        logger.warn(f"{self.short_id}> {self.name}.")

        # for a in self.head_agents:
        #     #name = a.__class__.__name__
        #     # self.publish(topic='terminate', payload=name)            

        # for a in self.body_agents:
        #     # name = a.__class__.__name__
        #     # self.publish(topic='terminate', payload=name)

        self._terminate_lock.set()



# ==================================
#  Implementation of BrokerNotifier 
# ==================================


    # For overriding
    # def on_echo_response(self, resp):
    #     pass
    
    
    def echo(self, topic, echo_handler):
        # logger.debug(f"topic: {topic}")
        self._echo_handlers[topic] = echo_handler
        self.publish(topic='system.echo', payload=topic)


    def _handle_echo(self, topic:str, payload):
        echo_topic = payload.decode('utf-8')
        # logger.debug(f"topic: {topic}, echo_topic: {echo_topic}")
        if echo_topic in self.subscribed_topics:
            resp = {
                'topic': echo_topic,
                'agent_id': self.agent_id,
            }
            self.publish('system.echo_response', json.dumps(resp))
        

    def _handle_echo_response(self, topic:str, payload):
        resp = json.loads(payload.decode('utf-8'))
        if echo_handler := self._echo_handlers.get(resp['topic']):
            echo_handler(resp)

    
    def _on_connect(self):
        logger.info(f"{self.short_id}> {self.name} Broker is connected.")
        
        self.subscribe("system.echo", topic_handler=self._handle_echo)
        self.subscribe("system.echo_response", topic_handler=self._handle_echo_response)
        self.subscribe("system.terminate", topic_handler=self.terminate)
        self.on_connected()
            
            
    def on_connected(self):
        pass


    @final
    def _on_message(self, topic:str, payload, source_payload=None):
        if topic in self._topic_handlers:
            topic_handler = self._topic_handlers[topic]
            if len(inspect.signature(topic_handler).parameters) == 2:
                return self._topic_handlers[topic](topic, payload)
            else:
                return self._topic_handlers[topic](topic, payload, source_payload)
        else:
            if len(inspect.signature(self.on_message).parameters) == 2:
                return self.on_message(topic, payload)
            else:
                return self.on_message(topic, payload, source_payload)


    def on_message(self, topic:str, payload, payload_info=None):
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
            logger.error(f"{self.short_id}> Type: {type(ex)}")
            logger.exception(ex)
            data = ""
            
        return data.strip()
        