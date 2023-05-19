from holon.HolonicAgent import HolonicAgent
from hearing.Microphone import Microphone
from hearing.BackgroundDenoising import BackgroundDenoising

class Hearing(HolonicAgent) :
    def __init__(self):
        super().__init__()
        self.head_agents.append(Microphone())
        self.body_agents.append(BackgroundDenoising())

if __name__ == '__main__':
    print('***** Hearing start *****')

    a = Hearing()
    a.start()
    