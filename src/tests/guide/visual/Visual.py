from holon.HolonicAgent import HolonicAgent
from visual.Camera import Camera
from visual.ImagePreprocessing import ImagePreprocessing

class Visual(HolonicAgent) :
    def __init__(self):
        super().__init__()
        self.head_agents.append(Camera())
        self.body_agents.append(ImagePreprocessing())
