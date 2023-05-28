# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging

from src.holon import Helper
from src.holon import config
from src.holon.HolonicAgent import HolonicAgent
from hearing.Microphone import Microphone
from hearing.VoiceToText import VoiceToText
# from tests.guide.hearing.Microphone import Microphone
# from tests.guide.hearing.VoiceToText import VoiceToText

class Hearing(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.head_agents.append(Microphone(cfg))
        # self.body_agents.append(VoiceToText(cfg))


if __name__ == '__main__':
    Helper.init_logging(config.log_dir, config.log_level)
    logging.info('***** Hearing start *****')
    a = Hearing()
    a.start()
