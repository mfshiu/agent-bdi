from datetime import datetime as dt
import logging
import os

from src.holon.HolonicAgent import HolonicAgent
from src.holon import config
import guide_config

class Speaker(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("voice.wave")

        super()._on_connect(client, userdata, flags, rc)


    def _on_message(self, client, db, msg):
        if "voice.wave" == msg.topic:
            try:
                filepath = dt.now().strftime("tests/_output/wave-%m%d-%H%M-%S.wav")
                with open(filepath, "wb") as file:
                    file.write(msg.payload)
                
            except Exception as ex:
                logging.exception(ex)


if __name__ == '__main__':
    logging.info('***** VoiceToText start *****')

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