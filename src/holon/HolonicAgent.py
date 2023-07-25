import inspect
import logging
from multiprocessing import Process
import os
import signal
import sys
import threading
import time 

import paho.mqtt.client as mqtt

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from holon import Helper
from core.Agent import Agent
from holon.Blackboard import Blackboard
from holon.HolonicDesire import HolonicDesire
from holon.HolonicIntention import HolonicIntention
from holon import config

logger = logging.getLogger('ABDI')

class HolonicAgent(Agent) :
    def __init__(self, cfg:config=None, b:Blackboard=None, d:HolonicDesire=None, i: HolonicIntention=None):
        b = b or Blackboard()
        d = d or HolonicDesire()
        i = i or HolonicIntention()
        super().__init__(b, d, i)
        self.head_agents = []
        self.body_agents = []
        self.run_interval_seconds = 1
        self._mqtt_client = None
        self._agent_proc = None
        self._config = cfg if cfg else config()
        self.name = f'<{self.__class__.__name__}>'


    def start(self):
        self._agent_proc = Process(target=self._run, args=(self._config,))
        self._agent_proc.start()

        for a in self.head_agents:
            a.start()
        for a in self.body_agents:
            a.start()

# ===================================
# |            Process              |
# ===================================


    def is_running(self):
        return not self._terminate_lock.is_set()

    def _on_connect(self, client, userdata, flags, rc):
        logger.info(f"{self.name} result code:{str(rc)}")
        client.subscribe("echo")
        client.subscribe("terminate")

        self._on_connected()


    def _on_connected(self):
        pass


    def _on_message(self, client, db, msg):
        data = msg.payload.decode('utf-8', 'ignore')
        self._on_topic(msg.topic, data)
        # try:
        #     self._on_topic(msg.topic, data)
        # except Exception as ex:
        #     logging.exception(f'{ex}')


    def _on_topic(self, topic, data):
        # logging.debug(f"{self.name} topic:{topic}, data:{data}")

        if "terminate" == topic:
            if data:
                if type(self).__name__ == data:
                    self.terminate()
            else:
                self.terminate()


    def _run_begin(self):
        #Helper.init_logging(self._config.log_dir, self._config.log_level)
        logger.debug(f"{self.name} ...")
        
        def signal_handler(signal, frame):
            logger.warning(f"{self.name} Ctrl-C: {self.__class__.__name__}")
            self.terminate()
        signal.signal(signal.SIGINT, signal_handler)

        self._terminate_lock = threading.Event()
        self._start_mqtt()
        threading.Thread(target=self.__interval_loop).start()
        
        # self.is_running = True
        # Helper.write_log("_run_begin 2")

    def __interval_loop(self):
        while not self._terminate_lock.is_set():
            self._run_interval()
            time.sleep(self.run_interval_seconds)

    def _run_interval(self):
        pass

    def _running(self):
        logger.debug(f"{self.name} ...")

    def _run(self, cfg:config):
        self._config = cfg
        self._run_begin()
        self._running()
        self._run_end()
    
    def _run_end(self):
        logger.debug(f"{self.name} ...")
        # self.is_running = False
        # self._terminate_lock.wait()
        while not self._terminate_lock.is_set():
            self._terminate_lock.wait(1)
        self._stop_mqtt()


    def _start_mqtt(self):
        logger.debug(f"{self.name} ...")
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_message = self._on_message
        cfg = self._config
        if cfg.mqtt_username:
            self._mqtt_client.username_pw_set(cfg.mqtt_username, cfg.mqtt_password)
        logger.debug(f"addr:{cfg.mqtt_address} port:{cfg.mqtt_port} keep:{cfg.mqtt_keepalive}")
        self._mqtt_client.connect(cfg.mqtt_address, cfg.mqtt_port, cfg.mqtt_keepalive)
        self._mqtt_client.loop_start()


    def _stop_mqtt(self):
        logger.debug(f"{self.name} ...")
        self._mqtt_client.disconnect()
        self._mqtt_client.loop_stop()


    def publish(self, topic, payload=None):
        # logging.debug(f'{str(self._mqtt_client.socket())}, topic:{topic}, payload:{payload}')
        ret = self._mqtt_client.publish(topic, payload)
        # logging.debug(f'ret: {str(ret)}')
        

    def terminate(self):
        logger.warn(f"{self.name}.")

        for a in self.head_agents:
            name = a.__class__.__name__
            self.publish(topic='terminate', payload=name)

        for a in self.body_agents:
            name = a.__class__.__name__
            self.publish(topic='terminate', payload=name)

        self._terminate_lock.set()
