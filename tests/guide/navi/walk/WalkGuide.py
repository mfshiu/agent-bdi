from navi.walk.KanbanDetect import KanbanDetect
from navi.walk.RoadDetect import RoadDetect
from holon.HolonicAgent import HolonicAgent

class WalkGuide(HolonicAgent):
    def __init__(self):
        super().__init__()
        self.body_agents.append(KanbanDetect())
        self.body_agents.append(RoadDetect())


