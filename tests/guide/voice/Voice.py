from holon.HolonicAgent import HolonicAgent
from voice.Speaker import Speaker
from voice.ToneProcessing import ToneProcessing

class Voice(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.head_agents.append(Speaker(cfg))
        self.body_agents.append(ToneProcessing(cfg))
