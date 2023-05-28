from navi.VisualInput import VisualInput
from holon.HolonicAgent import HolonicAgent
from navi.RouteFind import RouteFind
from navi.walk.WalkGuide import WalkGuide

class NaviSystem(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.head_agents.append(VisualInput(cfg))
        self.body_agents.append(WalkGuide(cfg))
        self.body_agents.append(RouteFind(cfg))


