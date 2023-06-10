import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
import signal

from src.holon import Helper
from src.holon import config
from src.holon.HolonicAgent import HolonicAgent

from src.holon.HolonicAgent import HolonicAgent
# from visual.Visual import Visual
from hearing import Hearing
# from voice.Voice import Voice
from navi import Navigator
# from dialog import DialogSystem
import guide_config

class GuideMain(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        # self.body_agents.append(DialogSystem(cfg))
        # self.head_agents.append(Visual())
        self.head_agents.append(Hearing(cfg))
        # self.head_agents.append(Voice())
        self.body_agents.append(Navigator(cfg))


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("guide.hearing.heared_text")

        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        if "guide.hearing.heared_text" == topic:
            if '系統關機' in data:
                self.terminate()

        super()._on_topic(topic, data)


if __name__ == '__main__':
    # Helper.init_logging()
    # logging.info('***** Main start *****')
    print('***** GuideMain start *****')

    def signal_handler(signal, frame):
        print("signal_handler")
    signal.signal(signal.SIGINT, signal_handler)

    cfg = config()
    cfg.mqtt_address = guide_config.mqtt_address
    cfg.mqtt_port = guide_config.mqtt_port
    cfg.mqtt_keepalive = guide_config.mqtt_keepalive
    cfg.mqtt_username = guide_config.mqtt_username
    cfg.mqtt_password = guide_config.mqtt_password
    cfg.log_level = guide_config.log_level
    cfg.log_dir = guide_config.log_dir    
    os.environ["OPENAI_API_KEY"] = guide_config.openai_api_key

    a = GuideMain(cfg)
    a.start()

    # time.sleep(5)
    # a.terminate()
