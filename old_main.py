import speech_recognition as sr
from gtts import gTTS
import os
from pydub import AudioSegment
from pydub.playback import play
from fuzzywuzzy import fuzz, process

from functions import get_today_date, get_live_temperature, get_time_in_urdu
import random

from responses import qa, negative_responses





def preprocess(text):
    return text.strip()


def get_best_match(question, qa_dict):
    question = preprocess(question)
    choices = {preprocess(k): k for k in qa_dict.keys()}
    best_match, score = process.extractOne(question, choices.keys(), scorer=fuzz.ratio)
    return choices[best_match] if score > 60 else None


def listen_to_mic():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio, language="ur-PK")
        print(f"Recognized Text: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        print("Could not request results; check your network connection.")
        return None


def speak_text(text):
    tts = gTTS(text=text, lang="ur")
    tts.save("response.mp3")
    response = AudioSegment.from_mp3("response.mp3")
    play(response)
    os.remove("response.mp3")


def main():
    print("Please ask a question...")
    user_input = listen_to_mic()

    if user_input is not None:
        best_match = get_best_match(user_input, qa)
        if best_match is not None and best_match in qa:
            response = qa[best_match]
            print(f"Response: {response}")
            if callable(response):
                speak_text(response())
            else:
                speak_text(response)
    else:
        print("I don't know the answer to that question.")
        speak_text(random.choice(negative_responses))


if __name__ == "__main__":
    main()
