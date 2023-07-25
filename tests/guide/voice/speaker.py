from datetime import datetime as dt
import logging
import os

import wave
import pyaudio
from playsound import playsound

from src.holon.HolonicAgent import HolonicAgent
from src.holon import logger


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
                playsound(filepath)
                os.remove(filepath)
            except Exception as ex:
                logger.exception(ex)
