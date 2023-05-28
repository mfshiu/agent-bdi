import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import multiprocessing
import signal

import logging

from src.holon import Helper
from src.holon import config
from src.holon.HolonicAgent import HolonicAgent
from tests.dialog.nlu import Nlu
from tests.dialog.AudioInput import AudioInput
import dialog_config
# from dialog.nlu import Nlu
# from dialog.AudioInput import AudioInput
# from dialog.AudioOutput import AudioOutput


class DialogSystem(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        # self.head_agents.append(AudioOutput())
        self.body_agents.append(AudioInput(cfg))
        self.body_agents.append(Nlu(cfg))
        
        
    def _on_topic(self, topic, data):
        if "guide.hearing.heared_text" == topic:
            if '系統關機' in data:
                self.terminate()

        super()._on_topic(topic, data)


if __name__ == '__main__':
    print('***** Dialog start *****')

    def signal_handler(signal, frame):
        print("signal_handler")
    signal.signal(signal.SIGINT, signal_handler)

    cfg = config()
    cfg.mqtt_address = dialog_config.mqtt_address
    cfg.mqtt_port = dialog_config.mqtt_port
    cfg.mqtt_keepalive = dialog_config.mqtt_keepalive
    cfg.mqtt_username = dialog_config.mqtt_username
    cfg.mqtt_password = dialog_config.mqtt_password
    cfg.log_level = dialog_config.log_level
    cfg.log_dir = dialog_config.log_dir    
    os.environ["OPENAI_API_KEY"] = dialog_config.openai_api_key

    multiprocessing.set_start_method('spawn')

    a = DialogSystem(cfg)
    a.start()
