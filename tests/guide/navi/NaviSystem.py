from guide.navi.VisualInput import VisualInput
from holon.HolonicAgent import HolonicAgent
from guide.navi.RouteFind import RouteFind
from guide.navi.walk.WalkGuide import WalkGuide

class NaviSystem(HolonicAgent) :
    def __init__(self):
        super().__init__()
        self.head_agents.append(VisualInput())
        self.body_agents.append(WalkGuide())
        self.body_agents.append(RouteFind())


