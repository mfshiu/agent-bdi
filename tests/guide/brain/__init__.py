from src.holon import logger
from src.holon.HolonicAgent import HolonicAgent
from navi import Navigator
from brain.greeting import Greeting

class Brain(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.body_agents.append(Navigator(cfg))
        self.body_agents.append(Greeting(cfg))


    def _on_connect(self, client, userdata, flags, rc):
        # client.subscribe("dialog.knowledge")
        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        super()._on_topic(topic, data)
