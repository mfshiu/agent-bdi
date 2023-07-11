import os
# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import logging

from src.holon import logger
from src.holon.HolonicAgent import HolonicAgent
import dialog.nlu.chatgpt as chatgpt
# import DialogSession

class Nlu(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        # self.head_agents.append(DialogSession())

        self.last_sentence = ""


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("hearing.trans.text")
        client.subscribe("voice.text")

        chatgpt.set_openai_api_key(os.getenv('OPENAI_API_KEY'))
        
        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        if "hearing.trans.text" == topic:
            logger.debug(f"{self.name} heared '{data}'")
            knowledge = self._understand(data, self.last_sentence)
            # self.publish("dialog.nlu.triplet", str(knowledge[1]))
            self.publish("dialog.knowledge", str(knowledge))
            logger.info(f"Understand: {knowledge}")
        elif "voice.text" == topic:
            logger.info(f"System ask: {data}")
            self.last_sentence = data

        super()._on_topic(topic, data)


    def _understand(self, sentence, last_sentence):
        try:
            knowledge = chatgpt.understand(sentence, last_sentence)
            # logger.info(f'knowledge: {knowledge}')
        except Exception as ex:
            knowledge = None
            logger.exception(f"Error: {str(ex)}")
        return knowledge


# if __name__ == '__main__':
#     Helper.init_logging()
#     logger.info('***** Hearing start *****')
#     a = Hearing()
#     a.start()
