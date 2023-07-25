import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from datetime import datetime as dt
import queue
from multiprocessing import Process
import time

import logging
import whisper
import torch

from src.holon.HolonicAgent import HolonicAgent
from src.holon import config
import guide_config

device = "cuda" if torch.cuda.is_available() else "cpu"
# whisper.DecodingOptions(language="zh")
global whisper_model
whisper_model = whisper.load_model("small", device=device)
# whisper_model = whisper.load_model("medium", device=device)

class Transcriptionist(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("hearing.voice")
        client.subscribe("trans.test")

        super()._on_connect(client, userdata, flags, rc)


    def _on_message(self, client, db, msg):
        if "hearing.voice" == msg.topic:
            wave_path = dt.now().strftime("tests/_input/voice-%m%d-%H%M-%S.wav")
            # logging.debug(f'data: {data}')
            with open(wave_path, "wb") as file:
                file.write(msg.payload)
            self.wave_queue.put(wave_path)
        elif "trans.test" == msg.topic:
            self.publish("trans.test", 'publish ')


    def _run_begin(self):
        super()._run_begin()
        logging.info(f"device:{device}")
        self.wave_queue = queue.Queue()


    def _running(self):
        global whisper_model
        while self.is_running():
            if self.wave_queue.empty():
                time.sleep(.1)
                continue
            try:
                wave_path = self.wave_queue.get()
                logging.debug(f'transcribing wave_path: {wave_path}')
                result = whisper_model.transcribe(wave_path)
                logging.debug(f'result: {result}')
                # transcribed_text = str(result["text"].encode('utf-8'))[2:-1].strip()
                transcribed_text = result["text"]
                # logging.debug(f'running addr: {self._config.mqtt_address}')
                self.publish("hearing.trans.text", transcribed_text)        
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
                
    def test1(self):
        # global whisper_model
        wh = whisper.load_model("small", device='cuda')
        wave_path = 'tests/_input/voice-0622-2323-31.wav'
        text = wh.transcribe(wave_path)
        # text = whisper_model.transcribe(wave_path)
        print(f'text: {text}')
            
            
    def test(self):    
        proc = Process(target=self.test1)
        proc.start()
        # self.test1()

if __name__ == '__main__':
    pass
