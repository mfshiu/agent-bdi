import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import signal

from src.holon import config
import guide_config
from voice.speaker import Speaker


if __name__ == '__main__':
    # Helper.init_logging()
    # logging.info('***** Main start *****')
    print('***** RunSpeaker start *****')

    def signal_handler(signal, frame):
        print("signal_handler")
    signal.signal(signal.SIGINT, signal_handler)

    cfg = config()
    cfg.mqtt_address = guide_config.mqtt_address
    cfg.mqtt_port = guide_config.mqtt_port
    cfg.mqtt_keepalive = guide_config.mqtt_keepalive
    cfg.mqtt_username = guide_config.mqtt_username
    cfg.mqtt_password = guide_config.mqtt_password
    cfg.log_level = guide_config.log_level
    cfg.log_dir = guide_config.log_dir    
    os.environ["OPENAI_API_KEY"] = guide_config.openai_api_key

    a = Speaker(cfg)
    a.start()

    # time.sleep(5)
    # a.terminate()
