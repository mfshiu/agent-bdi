import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime as dt
import multiprocessing
import queue
import signal
import time

import logging
import whisper
import torch

from src.holon.HolonicAgent import HolonicAgent
from src.holon import config
import dialog_config

device = "cuda" if torch.cuda.is_available() else "cpu"
# whisper.DecodingOptions(language="zh")
# whisper_model = whisper.load_model("tiny", device=device)
# whisper_model = whisper.load_model("base", device=device)
whisper_model = whisper.load_model("small", device=device)
# whisper_model = whisper.load_model("medium", device=device)
# whisper_model = whisper.load_model("large", device=device)

class AudioInput(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("record_wave")

        super()._on_connect(client, userdata, flags, rc)


    def _on_message(self, client, db, msg):
        if "record_wave" == msg.topic:
            # print(f"aa")
            # result = whisper_model.transcribe('tests/dialog/record-0529-0617-27.wav')
            # print(f"qq {result}")
            # logging.debug(f"wave_path:{data}")
            wave_path = dt.now().strftime("./tests/_output2/record-%m%d-%H%M-%S.wav")
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
                # print(".", end='')
                time.sleep(.1)
                continue
            try:
                wave_path = self.wave_queue.get()
                # wave_path = "./tests/dialog/record1.wav"
                logging.debug(f"transcribing wave_path:{wave_path}")
                result = whisper_model.transcribe(wave_path)
                # transcribed_text = str(result["text"].encode('utf-8'))[2:-1].strip()
                # result = {"text": "I would like to dinner"}
                transcribed_text = result["text"]
                logging.debug(f"transcribed_text: {transcribed_text}")
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

    # def start(self):
    #     super().start()

if __name__ == '__main__':
    logging.info('***** AudioInput start *****')
    # result = whisper_model.transcribe('tests/dialog/record-0529-0617-27.wav')
    # print(result)
    
    def signal_handler(signal, frame):
        print("signal_handler")
    signal.signal(signal.SIGINT, signal_handler)

    cfg = config()
    cfg.mqtt_address = dialog_config.mqtt_address
    cfg.mqtt_port = dialog_config.mqtt_port
    cfg.mqtt_keepalive = dialog_config.mqtt_keepalive
    cfg.mqtt_username = dialog_config.mqtt_username
    cfg.mqtt_password = dialog_config.mqtt_password
    cfg.log_level = dialog_config.log_level
    cfg.log_dir = dialog_config.log_dir    
    os.environ["OPENAI_API_KEY"] = dialog_config.openai_api_key

    a = AudioInput(cfg)
    a.start()
