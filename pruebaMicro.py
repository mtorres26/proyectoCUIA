import speech_recognition as sr

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Please say something...")
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio, language="es-ES")
        print("You said: {}".format(text))
    except sr.RequestError:
        print("API unavailable")
    except sr.UnknownValueError:
        print("Unable to recognize speech")

if __name__ == "_main_":
    recognize_speech_from_mic()
