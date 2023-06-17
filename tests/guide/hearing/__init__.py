import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging

from src.holon import Helper
from src.holon import config
from src.holon.HolonicAgent import HolonicAgent
from hearing.microphone import Microphone
# from hearing.VoiceToText import VoiceToText
# from tests.guide.hearing.microphone import Microphone
# from tests.guide.hearing.VoiceToText import VoiceToText

class Hearing(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.head_agents.append(Microphone(cfg))
        # self.body_agents.append(VoiceToText(cfg))


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("microphone.wave_path")

        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        if "microphone.wave_path" == topic:
            filepath = data
            logging.debug(f"wave_path:{filepath}")
            with open(filepath, "rb") as file:
                file_content = file.read()
            self.publish("hearing.voice", file_content)
            os.remove(filepath)

        super()._on_topic(topic, data)


if __name__ == '__main__':
    Helper.init_logging(config.log_dir, config.log_level)
    logging.info('***** Hearing start *****')
    a = Hearing()
    a.start()
