import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import logging

from src.holon import Helper
from src.holon.HolonicAgent import HolonicAgent
from Microphone import Microphone
from VoiceToText import VoiceToText

class Hearing(HolonicAgent) :
    def __init__(self):
        super().__init__()
        self.head_agents.append(Microphone())
        self.body_agents.append(VoiceToText())


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("record_text")

        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        if "record_text" == topic:
            if '系統關機' in data:
                self.terminate()

        super()._on_topic(topic, data)


if __name__ == '__main__':
    Helper.init_logging()
    logging.info('***** Hearing start *****')
    a = Hearing()
    a.start()
