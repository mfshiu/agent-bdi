import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from multiprocessing import Process
import signal
import threading
import time

from src.holon.HolonicAgent import HolonicAgent

class TestAgent(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)

def proc_run():
    def signal_handler(signal, frame):
        print("signal_handler 1")
        _terminate_lock.set()
        exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    _terminate_lock = threading.Event()
    while not _terminate_lock.is_set():
        _terminate_lock.wait(1)
    # _terminate_lock.wait()
    # while not _terminate_lock.is_set():
    #     time.sleep(0.1)
    # while True:
    #     time.sleep(0.1)

if __name__ == '__main__':
    # Helper.init_logging()
    # logging.info('***** Main start *****')
    print('***** Test start *****')

    # def signal_handler(signal, frame):
    #     a.terminate()
    #     print('***** TestAgent stop *****')
    #     exit(0)
    # signal.signal(signal.SIGINT, signal_handler)
    def signal_handler(signal, frame):
        print("signal_handler")
        # exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    a = TestAgent()
    a.start()
    # p = Process(target=proc_run)
    # p.start()
    # p1 = Process(target=proc_run)
    # p1.start()

    print('***** Test STOP *****')

    # while True:
    #     time.sleep(1)
