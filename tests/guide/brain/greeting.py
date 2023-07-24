import ast
import threading

from src.holon import logger
from src.holon.HolonicAgent import HolonicAgent
from brain import brain_helper


class Greeting(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("greeting.knowledge")

        # self.publish('brain.register_subject', 'greeting')
        threading.Timer(1, lambda: self.publish('brain.register_subject', 'greeting')).start()
        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        if "greeting.knowledge" == topic:
            knowledge = ast.literal_eval(data)
            if knowledge[0][1] == 'normal':
                brain_helper.speak(self, f'Hello, have a good day.')
            elif knowledge[0][1] == 'happy':
                brain_helper.speak(self, f'Wonderful, very nice to meet you.')
            else:
                logger.info(f'Uknown greeting mood.')
            self.publish('brain.subject_done')

        super()._on_topic(topic, data)


    def terminate(self):
        self.publish('brain.unregister_subject', 'greeting')
        super().terminate()