import os
from datetime import datetime as dt

from TTS.api import TTS

from src.holon import logger
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
        self.tts = TTS(model_name=self.models[7], gpu=True)

        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        if "voice.text" == topic:
            filepath = dt.now().strftime("tests/_output/voice-%m%d-%H%M-%S.wav")
            logger.debug(f"voice_path:{filepath}")
            try:
                self.tts.tts_to_file(text=data, file_path=filepath)
                with open(filepath, "rb") as file:
                    file_content = file.read()
                self.publish("voice.wave", file_content)
                os.remove(filepath)
            except Exception as ex:
                logger.exception(ex)

        super()._on_topic(topic, data)
