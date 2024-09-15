import pygame
from gtts import gTTS
import time
import speech_recognition as sr
import threading
from listener import listen_and_respond
from speak import speak_text
from mutagen.mp3 import MP3

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 480
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("dhyan")

# Colors
black = (0, 0, 0)

# Function to scale images while maintaining the aspect ratio
def scaled_image(image_path, target_width, target_height):
    image = pygame.image.load(image_path)
    image_ratio = image.get_width() / image.get_height()
    target_ratio = target_width / target_height
    if image_ratio > target_ratio:
        new_width = target_width
        new_height = int(target_width / image_ratio)
    else:
        new_width = int(target_height * image_ratio)
        new_height = target_height
    print(new_width, new_height)
    return pygame.transform.scale(image, (new_width, new_height))

# Load images
aspect_x = width//2
aspect_y = height//2
eye_idle = scaled_image("sprites/eyes/idle.png", aspect_x, aspect_y)
eye_blink = scaled_image("sprites/eyes/blink.png", aspect_x, aspect_y)
eye_recognizing = scaled_image("sprites/eyes/processing.png", aspect_x, aspect_y)
eye_music = scaled_image("sprites/eyes/music.png", aspect_x, aspect_y)

mouth_idle = scaled_image("sprites/mouth/idle.png", aspect_x, aspect_y)
mouth_recognizing = scaled_image("sprites/mouth/listening.png", aspect_x, aspect_y)
mouth_talking = scaled_image("sprites/mouth/talking.png", aspect_x, aspect_y)

# Clock to control the frame rate
clock = pygame.time.Clock()

# State variables
state = "idle"
last_blink = time.time()
blink_interval = 5  # seconds
blink_duration = 0.1  # seconds

# Talking timer variables
talking_start_time = 0
talking_duration = 2  # seconds
talking_image_interval = 0.1  # seconds
talking_image_switch_time = 0

# Function to draw the robot face
def draw_robot_face(eye_image, mouth_image):
    screen.fill(black)  # Black background
    eye_rect = eye_image.get_rect(center=(aspect_x, aspect_y - eye_image.get_height()//4))
    mouth_rect = mouth_image.get_rect(center=(aspect_x, aspect_y + mouth_image.get_height()//4))
    screen.blit(eye_image, eye_rect)
    screen.blit(mouth_image, mouth_rect)
    pygame.display.flip()

# Main loop
running = True
lip_open = True
speech_duration = 0
start_time = 0

def on_listening():
    global state
    state = "idle"

def on_recognizing():
    global state
    state = "recognizing"

def on_fail():
    global state
    state = "idle"

def on_play(audio):
    global state
    global speech_duration
    global start_time

    state = "talking"
    audio_file = MP3(audio)
    speech_duration = audio_file.info.length
    start_time = time.time()
    pygame.mixer.music.load(audio)
    pygame.mixer.music.play()

def play_music(audio):
    global state
    global speech_duration
    global start_time

    state = "music"
    audio_file = MP3(audio)
    speech_duration = 3
    start_time = time.time()
    pygame.mixer.music.load(audio)
    pygame.mixer.music.play()

def on_response(response):
    if isinstance(response, dict):
        if response["type"] == "text":
            speak_text(response["fn"](), on_play)
        elif response["type"] == "music":
            speak_text("ہاں! میں آپ کو سُناتی ہوں", on_play)
            time.sleep(3)
            play_music(response["fn"]())
    else:
        speak_text(response, on_play)

def listen_thread():
    while running:
        listen_and_respond(on_listening, on_recognizing, on_fail, on_response)
        time.sleep(speech_duration)

thread = threading.Thread(target=listen_thread)
thread.start()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            width, height = event.w, event.h
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            aspect_x = width//2
            aspect_y = height//2
            eye_idle = scaled_image("sprites/eyes/idle.png", aspect_x, aspect_y)
            eye_blink = scaled_image("sprites/eyes/blink.png", aspect_x, aspect_y)
            eye_recognizing = scaled_image("sprites/eyes/processing.png", aspect_x, aspect_y)
            eye_music = scaled_image("sprites/eyes/music.png", aspect_x, aspect_y)
            mouth_idle = scaled_image("sprites/mouth/idle.png", aspect_x, aspect_y)
            mouth_recognizing = scaled_image("sprites/mouth/listening.png", aspect_x, aspect_y)
            mouth_talking = scaled_image("sprites/mouth/talking.png", aspect_x, aspect_y)

    current_time = time.time()
    if state == "idle":
        if current_time - last_blink > blink_interval:
            state = "blink"
            last_blink = current_time
        else:
            draw_robot_face(eye_idle, mouth_idle)

    elif state == "blink":
        if current_time - last_blink < blink_duration:
            draw_robot_face(eye_blink, mouth_idle)
        else:
            state = "idle"
            last_blink = current_time

    elif state == "recognizing":
        draw_robot_face(eye_recognizing, mouth_recognizing)

    elif state == "talking":
        elapsed_time = current_time - start_time
        if elapsed_time < speech_duration:
            if current_time - talking_image_switch_time > talking_image_interval:
                talking_image_switch_time = current_time
                if lip_open:
                    draw_robot_face(eye_idle, mouth_talking)
                else:
                    draw_robot_face(eye_idle, mouth_recognizing)
                lip_open = not lip_open
        else:
            state = "idle"

    elif state == "music":
        draw_robot_face(eye_music, mouth_idle)

    clock.tick(30)  # 30 frames per second

pygame.quit()
