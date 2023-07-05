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

    def __play_wave_file(self, file_path):
        logger.debug(f'Play wave: {file_path}')
        # Open the wave file
        wave_file = wave.open(file_path, 'rb')

        # Initialize PyAudio
        audio = pyaudio.PyAudio()

        # Open a new stream
        stream = audio.open(format=audio.get_format_from_width(wave_file.getsampwidth()),
                            channels=wave_file.getnchannels(),
                            rate=wave_file.getframerate(),
                            output=True)

        # Read data from the wave file and play it
        chunk_size = 1024
        data = wave_file.readframes(chunk_size)

        while data:
            stream.write(data)
            data = wave_file.readframes(chunk_size)

        # Close the stream and terminate PyAudio
        stream.stop_stream()
        stream.close()
        audio.terminate()

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
