# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging

from src.holon import Helper
from src.holon.HolonicAgent import HolonicAgent
from hearing.Microphone import Microphone
from hearing.VoiceToText import VoiceToText

class Hearing(HolonicAgent) :
    def __init__(self):
        super().__init__()
        self.head_agents.append(Microphone())
        self.body_agents.append(VoiceToText())


if __name__ == '__main__':
    Helper.init_logging()
    logging.info('***** Hearing start *****')
    a = Hearing()
    a.start()
