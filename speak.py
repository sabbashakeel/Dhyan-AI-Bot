from gtts import gTTS
import os


def speak_text(text, on_play):
    tts = gTTS(text=text, lang="ur")
    tts.save("response.mp3")
    # response = AudioSegment.from_mp3("response.mp3")
    on_play("response.mp3")
    os.remove("response.mp3")
