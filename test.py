import logging

from src.abdi_config import AbdiConfig
from src.holon.HolonicAgent import HolonicAgent



class TestAgent(HolonicAgent):
    def __init__(self, config):
        super().__init__(config)
        self.head_agents.append(TestAgent2(config = config))


    def _run_interval(self):
        print(".", end="", flush=True)



class TestAgent2(HolonicAgent):
    # def __init__(self, cfg):
    #     super().__init__(cfg)


    def _run_interval(self):
        print(":", end="", flush=True)
    


if __name__ == '__main__':
    print('***** TestAgent start *****')

    a = TestAgent(config = AbdiConfig())
    a.start(head=True)


