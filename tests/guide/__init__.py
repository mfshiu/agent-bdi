import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
from logging.handlers import TimedRotatingFileHandler
import signal

from src.holon import Helper
from src.holon import config
from src.holon.HolonicAgent import HolonicAgent

from src.holon.HolonicAgent import HolonicAgent
# from visual.Visual import Visual
from hearing import Hearing
from voice import Voice
from navi import Navigator
from dialog import DialogSystem
import guide_config

class GuideMain(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.body_agents.append(DialogSystem(cfg))
        # self.head_agents.append(Visual())
        self.head_agents.append(Hearing(cfg))
        self.head_agents.append(Voice(cfg))
        self.body_agents.append(Navigator(cfg))


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("guide.hearing.heared_text")
        client.subscribe("dialog.nlu.triplet")

        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        if "guide.hearing.heared_text" == topic:
            if '系統關機' in data:
                self.terminate()
        # elif "dialog.nlu.triplet" == topic:
        #     logging.info(f'### {data} ###')

        super()._on_topic(topic, data)


if __name__ == 'xx__main__':
    def setup_logging(log_level):
        formatter = logging.Formatter(
            '%(levelname)1.1s %(asctime)s %(module)15s:%(lineno)03d %(funcName)15s) %(message)s',
            datefmt='%H:%M:%S')
        #logging.basicConfig(
            #level=logging.DEBUG,
            #format='%(levelname)1.1s %(asctime)s %(module)15s:%(lineno)03d %(funcName)15s) %(message)s',
            #datefmt='%H:%M:%S',
            #filename='/home/ericxu/work/_log/_abdi.log',
            #filemode='w'
        #)
        
        file_handler = TimedRotatingFileHandler('/home/ericxu/work/_log/abdi.log', when="d")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        
        logger = logging.getLogger('ABDI')
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger

    logger = setup_logging(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message')
    logger.error('Error message')
    logger.critical('Critical message')


if __name__ == 'x__main__':
    logger = Helper.init_logging(log_dir='/home/ericxu/work/_log', log_level=logging.DEBUG)
    logger.info(f'***** GuideMain start *****')
    from playsound import playsound
    playsound('/home/ericxu/work/test/file_example_WAV_1MG.wav')


if __name__ == '__main__':
    logger = Helper.init_logging(log_dir=guide_config.log_dir, log_level=guide_config.log_level)
    logger.info(f'***** GuideMain start *****')

    def signal_handler(signal, frame):
        print("signal_handler")
    signal.signal(signal.SIGINT, signal_handler)

    cfg = config()
    cfg.mqtt_address = guide_config.mqtt_address
    cfg.mqtt_port = guide_config.mqtt_port
    cfg.mqtt_keepalive = guide_config.mqtt_keepalive
    cfg.mqtt_username = guide_config.mqtt_username
    cfg.mqtt_password = guide_config.mqtt_password
    os.environ["OPENAI_API_KEY"] = guide_config.openai_api_key

    a = GuideMain(cfg)
    a.start()
