from holon.HolonicAgent import HolonicAgent
from guide.dialog.Nlu import Nlu
from guide.dialog.AudioInput import AudioInput
from guide.dialog.AudioOutput import AudioOutput

class DialogSystem(HolonicAgent) :
    def __init__(self):
        super().__init__()
        self.head_agents.append(AudioOutput())
        self.head_agents.append(AudioInput())
        self.body_agents.append(Nlu())
        

