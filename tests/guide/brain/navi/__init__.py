import ast
import threading

import Helper
from Helper import logger
from src.holon.HolonicAgent import HolonicAgent
from navi.VisualInput import VisualInput
from navi.RouteFind import RouteFind
from navi.walk.WalkGuide import WalkGuide
from brain import brain_helper

class Navigator(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.state = 0
        # self.head_agents.append(VisualInput(cfg))
        # self.body_agents.append(WalkGuide(cfg))
        # self.body_agents.append(RouteFind(cfg))


    def _on_connect(self, client, userdata, flags, rc):
        # client.subscribe("dialog.nlu.triplet")
        client.subscribe("go somewhere.knowledge")        
        threading.Timer(2, lambda: self._publish('brain.register_subject', 'go somewhere')).start()

        super()._on_connect(client, userdata, flags, rc)


    def __is_go(self, predict):
        logger.debug(f"predict: {predict}")
        result = ("go" == predict or "take" == predict)
        return result


    def __set_state(self, new_state):
        self.state = new_state
        logger.debug(f"New state: {new_state}")
       
    
    def __process_navi(self, knowledge):
        logger.debug(f"state: {self.state}, knowledge: '{knowledge}'")
        triplet = knowledge[1]
        if self.state == 0:
            self.target = triplet[2]
            brain_helper.speak(self, f"How about going to Dragon {self.target}?")
            self.__set_state(1)
        elif self.state == 1:
            if triplet[3]:
                brain_helper.speak(self, f"OK, let's go.")
                def arrive():
                    self.__set_state(0)
                    brain_helper.speak(self, f"We arrive the Dragon {self.target}.")
                    self._publish('brain.subject_done')
                threading.Timer(6, lambda: arrive()).start()
                self.__set_state(2)
            else:
                brain_helper.speak(self, f"Let me know if you want to go to the {self.target}.")
                self.__set_state(0)
                self._publish('brain.subject_done')
        elif self.state == 2:
            brain_helper.speak(self, f"We are on our way to Dragon {self.target}.")


    def _on_topic(self, topic, data):
        if "go somewhere.knowledge" == topic:
            knowledge = ast.literal_eval(data)
            # if (self.state == 0 and knowledge[0][0] == 'go somewhere') or self.state != 0:
                # logger.info(f"process: {data}")
                # if knowledge[0]
            self.__process_navi(knowledge)

        super()._on_topic(topic, data)


if __name__ == '__main__':
    Helper.init_logging()
    logger.info('***** Hearing start *****')
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
