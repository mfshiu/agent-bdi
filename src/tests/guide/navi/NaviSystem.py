from navi.VisualInput import VisualInput
from holon.HolonicAgent import HolonicAgent
from navi.RouteFind import RouteFind
from navi.walk.WalkGuide import WalkGuide

class NaviSystem(HolonicAgent) :
    def __init__(self):
        super().__init__()
        self.head_agents.append(VisualInput())
        self.body_agents.append(WalkGuide())
        self.body_agents.append(RouteFind())


