# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import logging

from src.holon import Helper
from src.holon.HolonicAgent import HolonicAgent
from navi.VisualInput import VisualInput
from navi.RouteFind import RouteFind
from navi.walk.WalkGuide import WalkGuide

class Navigator(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.head_agents.append(VisualInput(cfg))
        self.body_agents.append(WalkGuide(cfg))
        self.body_agents.append(RouteFind(cfg))
