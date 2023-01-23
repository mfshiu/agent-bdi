import logging
import inspect
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

class HolonicAgent(Agent) :
    def __init__(self, b:Blackboard=None, d:HolonicDesire=None, i: HolonicIntention=None):
        b = b or Blackboard()
        d = d or HolonicDesire()
        i = i or HolonicIntention()
        super().__init__(b, d, i)
        self.head_agents = []
        self.body_agents = []
        self.mqtt_client = None
        self.run_interval_seconds = 1
        self.is_running = False

    def _on_connect(self, client, userdata, flags, rc):
        logging.info(f"MQTT is connected with result code {str(rc)}")
        client.subscribe("echo")
        client.subscribe("terminate")

    def _on_message(self, client, db, msg):
        data = msg.payload.decode('utf-8', 'ignore')
        logging.debug("topic: %s, data: %s" % (msg.topic, data))

        if "terminate" == msg.topic:
            self._terminate_lock.set()
    
    def _run_begin(self):
        Helper.init_logging()
        logging.info(f"_run_begin: {self.__class__.__name__}")

        self._terminate_lock = threading.Event()
        self._start_mqtt()
        threading.Thread(target=self.__interval_loop).start()
        
        def signal_handler(signal, frame):
            self._terminate_lock.set()
        signal.signal(signal.SIGINT, signal_handler)
        
        self.is_running = True
        # Helper.write_log("_run_begin 2")

    def __interval_loop(self):
        while not self._terminate_lock.is_set():
            self._run_interval()
            time.sleep(self.run_interval_seconds)

    def _run_interval(self):
        pass

    def _running(self):
        logging.debug("running")

    def _run(self):
        self._run_begin()
        self._running()
        self._run_end()
    
    def _run_end(self):
        logging.warn(f"_run_end: {self.__class__.__name__}")
        self.is_running = False
        self._terminate_lock.wait()
        self._stop_mqtt()

    def _start_mqtt(self):
        logging.info("Starting...")
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        if config.mqtt_username:
            self.mqtt_client.username_pw_set(config.mqtt_username, config.mqtt_password)
        self.mqtt_client.connect(config.mqtt_address, config.mqtt_port, config.mqtt_keepalive)
        self.mqtt_client.loop_start()

    def _stop_mqtt(self):
        logging.warn("_stop_mqtt")
        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()
        
    def start(self):
        p = Process(target=self._run)
        p.start()

        for a in self.head_agents:
            logging.info(f"head: {a.__module__} start")
            a.start()
        for a in self.body_agents:
            logging.info(f"body: {a.__module__} start")
            a.start()
        



