import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from datetime import datetime as dt
import queue
import time

import logging
import whisper
import torch

from src.holon.HolonicAgent import HolonicAgent

device = "cuda" if torch.cuda.is_available() else "cpu"
# whisper.DecodingOptions(language="zh")
whisper_model = whisper.load_model("small", device=device)
# whisper_model = whisper.load_model("medium", device=device)

class AudioInput(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("record_wave")

        super()._on_connect(client, userdata, flags, rc)


    def _on_message(self, client, db, msg):
        if "record_wave" == msg.topic:
            # logging.debug(f"wave_path:{data}")
            wave_path = dt.now().strftime("tests/_output2/record-%m%d-%H%M-%S.wav")
            with open(wave_path, "wb") as file:
                file.write(msg.payload)
            logging.debug("File received and saved.")
            self.wave_queue.put(wave_path)
        else:
            super()._on_message(client, db, msg)

        # super()._on_topic(topic, data)


    # def _on_topic(self, topic, data):
    #     if "record_wave" == topic:
    #         # logging.debug(f"wave_path:{data}")
    #         wave_path = dt.now().strftime("tests/_output2/record-%m%d-%H%M-%S.wav")
    #         with open(wave_path, "wb") as file:
    #             file.write(data.payload)
    #         logging.debug("File received and saved.")
    #         self.wave_queue.put(wave_path)

    #     super()._on_topic(topic, data)


    def _run_begin(self):
        super()._run_begin()
        logging.info(f"device:{device}")
        self.wave_queue = queue.Queue()


    def _running(self):
        while self.is_running():
            if self.wave_queue.empty():
                time.sleep(.1)
                continue
            try:
                wave_path = self.wave_queue.get()
                result = whisper_model.transcribe(wave_path)
                # transcribed_text = str(result["text"].encode('utf-8'))[2:-1].strip()
                transcribed_text = result["text"]
                self.publish("guide.hearing.heared_text", transcribed_text)        
                logging.info(f">>> \033[33m{transcribed_text}\033[0m")
                if os.path.exists(wave_path):
                    os.remove(wave_path)
                logging.debug(f'Remained waves: {self.wave_queue.qsize()}')
            except queue.Empty:
                pass
            except UnicodeEncodeError:
                logging.info(f">>> \033[33m{transcribed_text.encode('utf-8')}\033[0m")
            except Exception as ex:
                _, exc_value, _ = sys.exc_info()
                logging.error(exc_value)


if __name__ == '__main__':
    logging.info('***** VoiceToText start *****')
    a = VoiceToText()
    a.start()
