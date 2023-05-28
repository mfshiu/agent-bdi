from holon.HolonicAgent import HolonicAgent
from visual.Camera import Camera
from visual.ImagePreprocessing import ImagePreprocessing

class Visual(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.head_agents.append(Camera(cfg))
        self.body_agents.append(ImagePreprocessing(cfg))
