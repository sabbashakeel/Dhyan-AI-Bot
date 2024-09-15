import speech_recognition as sr

from text import get_best_match
from responses import qa, negative_responses
import random


def listen_to_mic(on_listening, on_recognizing, on_fail):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Listening...")
        on_listening()
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        on_recognizing()
        text = recognizer.recognize_google(audio, language="ur-PK")
        print(f"Recognized Text: {text}")
        return text
    except sr.UnknownValueError:
        on_fail()
        print("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        print("Could not request results; check your network connection.")
        return None


def listen_and_respond(on_listening, on_recognizing, on_fail, on_response):
    user_input = listen_to_mic(on_listening, on_recognizing, on_fail)

    if user_input is not None:
        best_match = get_best_match(user_input, qa)
        print(f"Best Match: {best_match}")
        if best_match is not None and best_match in qa:
            response = qa[best_match]
            print(f"Response: {response}")
            on_response(response)
        else:
            on_response(random.choice(negative_responses))
    else:
        on_response(random.choice(negative_responses))
