import logging
import time

from holon.HolonicAgent import HolonicAgent
from visual.Visual import Visual
from hearing.Hearing import Hearing
from voice.Voice import Voice
from navi.NaviSystem import NaviSystem
from dialog.DialogSystem import DialogSystem

class GuideMain(HolonicAgent) :
    def __init__(self):
        super().__init__()
        self.body_agents.append(NaviSystem())
        self.body_agents.append(DialogSystem())
        self.head_agents.append(Visual())
        self.head_agents.append(Hearing())
        self.head_agents.append(Voice())

    def _run(self):
        logging.info(f"Run GuideMain")
        time.sleep(2)
