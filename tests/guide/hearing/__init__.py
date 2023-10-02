import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging

from src.holon import logger
from src.holon.HolonicAgent import HolonicAgent
from hearing.microphone import Microphone

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
            logger.debug(f"wave_path:{filepath}")
            try:
                with open(filepath, "rb") as file:
                    file_content = file.read()
                self._publish("hearing.voice", file_content)
                os.remove(filepath)
            except Exception as ex:
                logger.exception(ex)

        super()._on_topic(topic, data)
