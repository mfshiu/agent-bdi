from datetime import datetime as dt
import time

from holon.HolonicAgent import HolonicAgent

class Microphone(HolonicAgent) :
    def __init__(self):
        super().__init__()

    def _running(self):
        while self.is_running():
            print(f'Microphone...{dt.now()}')
            time.sleep(3)

if __name__ == '__main__':
    # Helper.init_logging()
    # logging.info('***** Main start *****')
    print('***** Microphone start *****')

    a = Microphone()
    a.start()
    
            
