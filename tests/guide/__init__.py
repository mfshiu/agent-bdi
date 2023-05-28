import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
import signal

from src.holon import Helper
from src.holon.HolonicAgent import HolonicAgent

from src.holon.HolonicAgent import HolonicAgent
# from visual.Visual import Visual
from hearing import Hearing
# from voice.Voice import Voice
# from navi.NaviSystem import NaviSystem
from dialog import DialogSystem

class GuideMain(HolonicAgent):
    def __init__(self):
        super().__init__()
        # self.body_agents.append(NaviSystem())
        self.body_agents.append(DialogSystem())
        # self.head_agents.append(Visual())
        self.head_agents.append(Hearing())
        # self.head_agents.append(Voice())


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

    a = GuideMain()
    a.start()

    # time.sleep(5)
    # a.terminate()
