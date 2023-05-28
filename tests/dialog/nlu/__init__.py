import os
# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import logging

from src.holon import Helper
from src.holon.HolonicAgent import HolonicAgent
from tests.lab import ChatComp2 as chatgpt
# import DialogSession

class Nlu(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        # self.head_agents.append(DialogSession())


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("guide.hearing.heared_text")
        chatgpt.set_openai_api_key(os.getenv('OPENAI_API_KEY'))
        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        if "guide.hearing.heared_text" == topic:
            logging.debug(f"{self.name} heared '{data}'")
            triplet = self._understand(data)
            logging.info(f"Understand: {triplet}")
            self.publish("dialog.nlu.triplet", str(triplet))
        super()._on_topic(topic, data)


    def _understand(self, sentence):
        try:
            triplet = chatgpt.understand(sentence)
        except Exception as ex:
            triplet = None
            logging.exception(f"Error: {str(ex)}")
        return triplet


# if __name__ == '__main__':
#     Helper.init_logging()
#     logging.info('***** Hearing start *****')
#     a = Hearing()
#     a.start()
