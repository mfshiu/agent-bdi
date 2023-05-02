from holon.HolonicAgent import HolonicAgent
from dialog.Nlu import Nlu
from dialog.AudioInput import AudioInput
from dialog.AudioOutput import AudioOutput

class DialogSystem(HolonicAgent) :
    def __init__(self):
        super().__init__()
        self.head_agents.append(AudioOutput())
        self.head_agents.append(AudioInput())
        self.body_agents.append(Nlu())
        

