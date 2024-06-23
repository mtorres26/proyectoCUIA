import cv2
import face_recognition
import pyaudio
import sounddevice
import speech_recognition as sr
import random
import threading
import time
import queue

# Función que añade a una cola lo que se dice por el micrófono
def escuchar(colaVoz, eventoVoz):
    r = sr.Recognizer()
    transcripcion = None
    while True:
        if eventoVoz.is_set():
            with sr.Microphone() as source:
                print("Escuchando...")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                print("Procesando...")
                try:
                    transcripcion = r.recognize_google(audio, language='es-ES')
                    print("Google Speech Recognition thinks you said " + transcripcion)
                except sr.UnknownValueError:
                    transcripcion = None
                except sr.RequestError:
                    transcripcion = None
                colaVoz.put(transcripcion)

def main():
    
    cv2.namedWindow("FutGuesser - Guess the football team.")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Couldn't open the camera. Exiting...")
        exit()
    
    