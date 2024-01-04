import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from datetime import datetime as dt
import threading

from src.holon import logger
import numpy as np
import pyaudio
import wave

from src.holon.HolonicAgent import HolonicAgent

# 配置音频录制参数
CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
MAX_RECORD_SECONDS = 10 * 60
SILENCE_THRESHOLD = (RATE // CHUNK) * 0.28

class Microphone(HolonicAgent):
    def __init__(self, cfg=None):
        super().__init__(cfg)


    def __compute_frames_mean(frames):
        def to_shorts(bytes):
            data = np.frombuffer(bytes, dtype=np.int16)
            return [x if x <= 32767 else 32767 - x for x in data]
        
        if not frames:
            return 0
        
        data = [x for x in to_shorts(frames) if x >= 0]
        audio_mean = 0 if len(data) == 0 else sum([int(x) for x in data]) // len(data)
        return audio_mean


    # def __is_silence(sound_raw):
    #     audio_mean = Microphone.__compute_frames_mean(sound_raw)
    #     #logging.debug(f'audio_mean: {audio_mean}')

    #     return (audio_mean < 200, audio_mean)
    

    def __wait_voice(self, audio_stream):
        first_frames = []
        logger.debug("for 60 second...")
        for _ in range(0, int(RATE / CHUNK * 60)):
            if not self.is_running():
                break
            # print(".", end="")
            try:
                sound_raw = audio_stream.read(CHUNK)
            except Exception as ex:
                logger.error("Read audio stream error!\n%s", str(ex))
                break

            if not Microphone.__compute_frames_mean(sound_raw) < 200:
                first_frames.append(sound_raw)  # 發現聲音
                if len(first_frames) > 2:
                    break                       # 確定開始發聲
            elif len(first_frames):
                    first_frames.clear()

        return first_frames if len(first_frames) else None
    

    def __record_to_silence(self, audio_stream):
        frames = []
        silence_count = 0
        total_mean = 0

        logger.debug("...")
        for i in range(0, int(RATE / CHUNK * MAX_RECORD_SECONDS)):
            if not self.is_running():
                break
            try:
                sound_raw = audio_stream.read(CHUNK)
            except Exception as ex:
                logger.error("Read audio stream error!\n%s", str(ex))
                break
            frames.append(sound_raw)

            mean = Microphone.__compute_frames_mean(sound_raw)
            total_mean += mean
            if mean < 200:
                silence_count += 1
                print('.', end='', flush=True)
            else:
                silence_count = 0
                print('^', end='', flush=True)
                # print(f'{mean}', end='', flush=True)
            if silence_count > SILENCE_THRESHOLD*1:
                print()
                logger.debug(f"silence_count:{silence_count}, frames: {len(frames)}")
                break

        frames_mean = total_mean // len(frames)
        logger.debug(f'frames mean: {frames_mean}')
        return frames, frames_mean


    def _record2(self):
        audio = pyaudio.PyAudio()
        audio_stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        
        frames = self.__wait_voice(audio_stream)
        frames_mean = 0
        if frames:
            other_frames, frames_mean = self.__record_to_silence(audio_stream)
            frames.extend(other_frames)
        # logging.debug(f'Average frames: {Microphone.__compute_frames_mean([byte for sublist in frames for byte in sublist])}')
        # logging.debug(f'Frames: {frames}')

        # Stop recording
        audio_stream.stop_stream()
        audio_stream.close()
        audio.terminate()

        wave_path = None
        if frames and len(frames) >= SILENCE_THRESHOLD//2 and frames_mean >= 500:
            
            def write_wave_file(wave_path, wave_data):
                logger.info(f"Write to file: {wave_path}...")
                wf = wave.open(wave_path, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                self.publish("microphone.wave_path", wave_path)                
                # test
                #playsound(wave_path)
                #os.remove(wave_path)

            wave_path = dt.now().strftime("tests/_output/record-%m%d-%H%M-%S.wav")
            threading.Thread(target=write_wave_file, args=(wave_path, b''.join(frames),)).start()
            # self.publish("microphone.wave_path", wave_path)
            # write_wave_file(wave_path, b''.join(frames))

        return wave_path


    def _running(self):
        while self.is_running():
            try:
                # filepath = self._record()
                filepath = self._record2()
                # if filepath:
                    # with open(filepath, "rb") as file:
                    #     file_content = file.read()
                    # self.publish("hearing.microphone.voice", file_content)
                    # os.remove(filepath)
                    # logging.debug(f'Publish: microphone.wave_path: {filepath}')
                    # self.publish("microphone.wave_path", filepath)
            except Exception as ex:
                logger.exception(ex)


    def _record(self):
        # 初始化Pyaudio
        audio = pyaudio.PyAudio()

        # 开始录制音频
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)

        frames = []
        logger.info("Start recording")
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            if (self.is_running()):
                # print(".", end="")
                data = stream.read(CHUNK)
                frames.append(data)

        # 停止录制音频
        stream.stop_stream()
        stream.close()
        audio.terminate()

        filepath = dt.now().strftime("tests/_output/record-%m%d-%H%M-%S.wav")
        def write_wave_file(filepath, wave_data):
            logger.debug("Write to file")
            wf = wave.open(filepath, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(wave_data)
            wf.close()
        # threading.Thread(target=write_wave_file, args=(filepath, b''.join(frames),)).start()
        write_wave_file(filepath, b''.join(frames))

        return filepath


if __name__ == '__main__':
    logger.info('***** Microphone start *****')
    a = Microphone()
    a.start()


# if __name__ == '__main__':
#     logging.info('***** Microphone Test *****')

#     a = Microphone()

#     audio = pyaudio.PyAudio()
#     audio_stream = audio.open(format=FORMAT, channels=CHANNELS,
#                         rate=RATE, input=True,
#                         frames_per_buffer=CHUNK)
    
#     first_frames = a._wait_voice(audio_stream)
#     print(f"first_frames: {first_frames}")

#     # 停止录制音频
#     audio_stream.stop_stream()
#     audio_stream.close()
#     audio.terminate()
