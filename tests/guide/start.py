import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# import logging
import signal
import time

from guide import GuideMain
# import Helper

if __name__ == '__main__':
    # Helper.init_logging()
    # logging.info('***** Main start *****')
    print('***** Main start *****')

    def signal_handler(signal, frame):
        print("signal_handler")
    signal.signal(signal.SIGINT, signal_handler)

    a = GuideMain()
    a.start()

    # time.sleep(5)
    # a.terminate()
