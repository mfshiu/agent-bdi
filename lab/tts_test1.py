from TTS.api import TTS

# Running a multi-speaker and multi-lingual model

# List available 🐸TTS models and choose the first one
models = TTS.list_models()
[print(f"{i} {name}") for i, name in enumerate(models)]
# model_name = models[30] # tts_models/zh-CN/baker/tacotron2-DDC-GST
# model_name = models[24] # tts_models/es/mai/tacotron2-DDC
model_name = models[6] # tts_models/en/ek1/tacotron2
print(f"model_name: {model_name}")
# Init TTS
tts = TTS(model_name=model_name, gpu=True)
print(f"tts.languages: {tts.languages}")
print(f"tts.speakers: {tts.speakers}")

# Run TTS

# ❗ Since this model is multi-speaker and multi-lingual, we must set the target speaker and the language
# Text to speech with a numpy output
# wav = tts.tts("This is a test! This is also a test!!", speaker=tts.speakers[0], language=tts.languages[0])
# Text to speech to a file
# tts.tts_to_file(text="Hello world!", speaker=tts.speakers[0], language=tts.languages[0], file_path="output.wav")
text = "我們的戰士沒有流一滴血。"
text = "普京發誓懲罰「武裝叛亂」 瓦格納回擊「換總統」。"
text = "一觸即發的俄羅斯內戰突然出現轉機。在白俄羅斯總統盧卡申科斡旋下，瓦格納領導人普里戈任發表聲明，同意停止進軍莫斯科，下令部隊返回大本營。"
text = "普里戈任在聲明中說:「我們踏上正義遊行，24小時內，移動了200公里前往達莫斯科。 在那段時間裡，我們的戰士沒有流一滴血。 現在已經到了流血的時刻了。 不過，我們明白有責任避免俄羅斯人流血，正根據計劃掉頭返回我們的大本營。"
text = "Dónde puedo cambiar dinero?"
text = "Me gustaría cambiar 50 dólares a euros."
text = "The weather today is good."
tts.tts_to_file(text=text, file_path="output3-1.wav")
