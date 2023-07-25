from TTS.api import TTS

# Running a multi-speaker and multi-lingual model

# List available 🐸TTS models and choose the first one
model_name = TTS.list_models()[0]
print(f"model_name: {model_name}")
# Init TTS
tts = TTS(model_name=model_name, gpu=True)
print(f"tts.languages: {tts.languages}")

# Run TTS

# ❗ Since this model is multi-speaker and multi-lingual, we must set the target speaker and the language
# Text to speech with a numpy output
wav = tts.tts("This is a test! This is also a test!!", speaker=tts.speakers[0], language=tts.languages[0])
# Text to speech to a file
tts.tts_to_file(text="Hello world!", speaker=tts.speakers[0], language=tts.languages[0], file_path="output.wav")
# tts.tts_to_file(text="我們的戰士沒有流一滴血", speaker=tts.speakers[0], language=tts.languages[0], file_path="output.wav")

# Running a single speaker model

# Init TTS with the target model name
tts = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False, gpu=True)
print(f"tts.languages: {tts.languages}")
# Run TTS
tts.tts_to_file(text="Ich bin eine Testnachricht.", file_path="output1.wav")

# Example voice cloning with YourTTS in English, French and Portuguese

tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progr0ess_bar=False, gpu=True)
print(f"tts.languages: {tts.languages}")
# tts.tts_to_file("This is voice cloning.", speaker_wav="my/cloning/audio.wav", language="en", file_path="output2-1.wav")
# tts.tts_to_file("C'est le clonage de la voix.", speaker_wav="my/cloning/audio.wav", language="fr-fr", file_path="output2-2.wav")
# tts.tts_to_file("Isso é clonagem de voz.", speaker_wav="my/cloning/audio.wav", language="pt-br", file_path="output2-3.wav")


# Example voice conversion converting speaker of the `source_wav` to the speaker of the `target_wav`

# tts = TTS(model_name="voice_conversion_models/multilingual/vctk/freevc24", progress_bar=False, gpu=True)
# tts.voice_conversion_to_file(source_wav="my/source.wav", target_wav="my/target.wav", file_path="output.wav")

# Example voice cloning by a single speaker TTS model combining with the voice conversion model. This way, you can
# clone voices by using any model in 🐸TTS.

# tts = TTS("tts_models/de/thorsten/tacotron2-DDC")
# tts.tts_with_vc_to_file(
#     "Wie sage ich auf Italienisch, dass ich dich liebe?",
#     speaker_wav="target/speaker.wav",
#     file_path="ouptut.wav"
# )

# Example text to speech using [🐸Coqui Studio](https://coqui.ai) models.

# You can use all of your available speakers in the studio.
# [🐸Coqui Studio](https://coqui.ai) API token is required. You can get it from the [account page](https://coqui.ai/account).
# You should set the `COQUI_STUDIO_TOKEN` environment variable to use the API token.

# If you have a valid API token set you will see the studio speakers as separate models in the list.
# The name format is coqui_studio/en/<studio_speaker_name>/coqui_studio
# models = TTS().list_models()
# # Init TTS with the target studio speaker
# tts = TTS(model_name="coqui_studio/en/Torcull Diarmuid/coqui_studio", progress_bar=False, gpu=False)
# print(f"tts.languages: {tts.languages}")
# # Run TTS
# tts.tts_to_file(text="This is a test.", file_path="output3-1.wav")
# # Run TTS with emotion and speed control
# tts.tts_to_file(text="This is a test.", file_path="output3-2.wav", emotion="Happy", speed=1.5)


# #Example text to speech using **Fairseq models in ~1100 languages** 🤯.

# #For these models use the following name format: `tts_models/<lang-iso_code>/fairseq/vits`.
# #You can find the list of language ISO codes [here](https://dl.fbaipublicfiles.com/mms/tts/all-tts-languages.html) and learn about the Fairseq models [here](https://github.com/facebookresearch/fairseq/tree/main/examples/mms).

# # TTS with on the fly voice conversion
# api = TTS("tts_models/deu/fairseq/vits")
# api.tts_with_vc_to_file(
#     "Wie sage ich auf Italienisch, dass ich dich liebe?",
#     speaker_wav="target/speaker.wav",
#     file_path="ouptut.wav"
# )