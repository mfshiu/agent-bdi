# import atexit
import inspect
from multiprocessing import Process
import os
import signal
import sys
import threading
import time 

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import logging

from abdi_config import AbdiConfig
from broker.notifier import BrokerNotifier
from broker.broker_maker import BrokerMaker
from core.Agent import Agent
from holon.Blackboard import Blackboard
from holon.HolonicDesire import HolonicDesire
from holon.HolonicIntention import HolonicIntention


logger = logging.getLogger("ABDI")

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
        self.run_interval_seconds = 1
        
        self.name = f'<{self.__class__.__name__}>'        
        self._agent_proc = None        
        self._broker = None


    def start(self, head=False):
        self._agent_proc = Process(target=self._run, args=(self.config,))
        self._agent_proc.start()
        
        # procs = [self._agent_proc]

        # for a in self.head_agents:
        #     procs.append(a.start())
        # for a in self.body_agents:
        #     procs.append(a.start())
        for a in self.head_agents:
            a.start()
        for a in self.body_agents:
            a.start()
        
        if head:
            try:
                self._agent_proc.join()
            except:
                logger.warning(f"{self.name} terminated.")
        # if head:
        #     try:
        #         self._agent_proc.join()
        #         # for proc in procs:
        #         #     proc.join()
        #     except:
        #         logger.warning(f"System terminated.")
        #     return None
        # else:
        #     return self._agent_proc


    # def start(self):
    #     logger.debug(f"...")
        
    #     self._agent_proc = Process(target=self._run, args=(self.config,))
    #     self._agent_proc.start()

    #     for a in self.head_agents:
    #         a.start()
    #     for a in self.body_agents:
    #         a.start()
            
    #     return self._agent_proc



# =====================
#  Instance of Process 
# =====================


    def _is_running(self):
        return not self._terminate_lock.is_set()


    def _run(self, config:AbdiConfig):
        self.config = config
        self._run_begin()
        self._running()
        self._run_end()
    

    def _run_begin(self):
        logger.debug(f"start")

        def signal_handler(signal, frame):
            logger.warning(f"{self.name} Ctrl-C: {self.__class__.__name__}")
            self._terminate()
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
                self._run_interval()
                time.sleep(self.run_interval_seconds)
        threading.Thread(target=interval_loop).start()
            
        logger.debug(f"done.")


    def _run_interval(self):
        pass


    def _running(self):
        logger.debug(f"Running ...")

    def _run_end(self):
        logger.debug(f"Run end ...")

        while not self._terminate_lock.is_set():
            self._terminate_lock.wait(1)

        self._broker.stop() 


    def _publish(self, topic, payload=None):
        return self._broker.publish(topic, payload)


    def _subscribe(self, topic, data_type="str"):
        return self._broker.subscribe(topic, data_type)
        

    def _terminate(self):
        logger.warn(f"{self.name}.")

        for a in self.head_agents:
            name = a.__class__.__name__
            self._publish(topic='terminate', payload=name)

        for a in self.body_agents:
            name = a.__class__.__name__
            self._publish(topic='terminate', payload=name)

        self._terminate_lock.set()



# ==================================
#  Implementation of BrokerNotifier 
# ==================================

    
    def _on_connect(self):
        logger.info(f"{self.name} Broker is connected.")
        
        self._subscribe("echo")
        self._subscribe("terminate")


    def _on_message(self, topic:str, payload):
        pass


    # def _on_topic(self, topic, data):
    #     if "terminate" == topic:
    #         if data:
    #             if type(self).__name__ == data:
    #                 self._terminate()
    #         else:
    #             self._terminate()



# ==================================
#  Others operation 
# ==================================


    def _convert_to_text(self, payload) -> str:
        if payload:
            data = payload.decode('utf-8', 'ignore')
        else:
            data = None
        
        return data
        