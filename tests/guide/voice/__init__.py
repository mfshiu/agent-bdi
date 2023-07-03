import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime as dt
import logging

from TTS.api import TTS

from src.holon import Helper
from src.holon import config
from src.holon.HolonicAgent import HolonicAgent
from voice.speaker import Speaker

class Voice(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.head_agents.append(Speaker(cfg))
        # self.body_agents.append(VoiceToText(cfg))


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("voice.text")

        self.models = TTS.list_models()
        self.tts = TTS(model_name=self.models[6], gpu=True)

        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        if "voice.text" == topic:
            filepath = dt.now().strftime("tests/_output/voice-%m%d-%H%M-%S.wav")
            logging.debug(f"voice_path:{filepath}")
            try:
                self.tts.tts_to_file(text=data, file_path=filepath)
                with open(filepath, "rb") as file:
                    file_content = file.read()
                self.publish("voice.wave", file_content)
                os.remove(filepath)
            except Exception as ex:
                logging.exception(ex)

        super()._on_topic(topic, data)


if __name__ == '__main__':
    Helper.init_logging(config.log_dir, config.log_level)
    logging.info('***** Voice start *****')
    a = Voice()
    a.start()
