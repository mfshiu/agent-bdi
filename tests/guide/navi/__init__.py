# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import ast
import logging

# import openai

from src.holon import Helper
from src.holon.HolonicAgent import HolonicAgent
from navi.VisualInput import VisualInput
from navi.RouteFind import RouteFind
from navi.walk.WalkGuide import WalkGuide

class Navigator(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        # self.head_agents.append(VisualInput(cfg))
        # self.body_agents.append(WalkGuide(cfg))
        # self.body_agents.append(RouteFind(cfg))


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("dialog.nlu.triplet")

        super()._on_connect(client, userdata, flags, rc)


    def __is_go(self, predict):
        logging.debug(f"predict: {predict}")
        result = "go" == predict
        return result


    def _on_topic(self, topic, data):
        if "dialog.nlu.triplet" == topic:
            logging.debug(f"process: '{data}'")
            triplet = ast.literal_eval(data.lower())
            logging.debug(f"triplet: '{triplet}'")
            if self.__is_go(triplet[1]):
                logging.debug(f"Let's go")

        super()._on_topic(topic, data)


if __name__ == '__main__':
    Helper.init_logging()
    logging.info('***** Hearing start *****')
    a = Navigator()
    ans = a.__is_go('go')
    print(f'Is go: {ans}')


    # def __is_go(self, predict):
    #     logging.debug(f"predict: {predict}")
    #     completion = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo",
    #         temperature=0,
    #         max_tokens=3,
    #         messages=[
    #                 {"role": "system", "content": "You are a word analyzer."},
    #                 {"role": "assistant", "content": "Check the word sentence to (subject) format following the rules below:"},
    #                 {"role": "assistant", "content": "1. Response only yes or no."},
    #                 {"role": "assistant", "content": "2. If there is no subject, infer the subject."},
    #                 {"role": "assistant", "content": "3. Respond ONLY in the requested format: (subject), without any other wrods."},
    #                 {"role": "assistant", "content": "4. Answer in English"},
    #                 {"role": "system", "name": "example_user", "content": "I want to go to the park."},
    #                 {"role": "system", "name": "example_assistant", "content": "(I)"},
    #                 {"role": "system", "name": "example_user", "content": "He's going to the bathroom."},
    #                 {"role": "system", "name": "example_assistant", "content": "(He)"},
    #                 {"role": "system", "name": "example_user", "content": "我晚餐想吃麥當勞漢堡。"},
    #                 {"role": "system", "name": "example_assistant", "content": "(I)"},
    #                 {"role": "system", "name": "example_user", "content": "terminate system."},
    #                 {"role": "system", "name": "example_assistant", "content": "(You)"},
    #                 {"role": "user", "content": f"Analyze: \"{predict}\", response only one word."},
    #             ]
    #     )

    #     resp = completion['choices'][0]['message']['content']
    #     logging.debug(f"resp: {resp}")
    #     return False
