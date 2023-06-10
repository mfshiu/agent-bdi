from multiprocessing import Process

from navi.walk.KanbanDetect import KanbanDetect
from navi.walk.RoadDetect import RoadDetect
from holon.HolonicAgent import HolonicAgent

class WalkGuide(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.body_agents.append(KanbanDetect(cfg))
        self.body_agents.append(RoadDetect(cfg))


    def start(self):
        self._agent_proc = Process(target=self._run, args=(self._config,))
        self._agent_proc.start()

        for a in self.head_agents:
            a.start()
        for a in self.body_agents:
            a.start()
