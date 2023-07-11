import ast

from src.holon import logger
from src.holon.HolonicAgent import HolonicAgent
from brain import brain_helper


class Greeting(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("dialog.knowledge")
        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        if "dialog.knowledge" == topic:
            knowledge = ast.literal_eval(data)
            if knowledge[0][0] == 'greeting':
                brain_helper.speak(self, f'Aloha')
        super()._on_topic(topic, data)
