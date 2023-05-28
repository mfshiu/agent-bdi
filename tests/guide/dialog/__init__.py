import logging

from src.holon import Helper
from src.holon.HolonicAgent import HolonicAgent
from dialog.nlu import Nlu
# from dialog.AudioOutput import AudioOutput

class DialogSystem(HolonicAgent) :
    def __init__(self):
        super().__init__()
        # self.head_agents.append(AudioOutput())
        self.body_agents.append(Nlu())
