# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import logging

from src.holon import Helper
from src.holon.HolonicAgent import HolonicAgent
from dialog.nlu import Nlu
# from tests.guide.dialog.AudioInput import AudioInput
# from dialog.nlu import Nlu
# from dialog.AudioInput import AudioInput
# from dialog.AudioOutput import AudioOutput

class DialogSystem(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        # self.head_agents.append(AudioOutput())
        # self.body_agents.append(AudioInput(cfg))
        self.body_agents.append(Nlu(cfg))
