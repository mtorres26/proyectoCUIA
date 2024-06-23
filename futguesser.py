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


# Función que devuelve un equipo de fútbol aleatorio
def randomTeam():
    teams = ["Bayern Munich", "Betis"]
    return teams[random.randint(0, 1)]


def main():
    team = randomTeam()
    equipment = cv2.imread(f"./img/{team}.png")

    cv2.namedWindow("FutGuesser - Guess the football team.")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Couldn't open the camera. Exiting...")
        exit()

    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fondo = cv2.resize(equipment, (ancho,alto))

    colaVoz = queue.Queue()

    # Inicializar threads de voz y de cara
    evento_voz = threading.Event()
    hilo_datos = threading.Thread(target=escuchar, daemon=True, args=(colaVoz, evento_voz))
    hilo_datos.start()

    respuesta = None

    # Bucle principal
    while cap.isOpened():
        ret, framebgr = cap.read()

        if not ret:
            print("Couldn't read the frame. Exiting...")
            break

        # Procesado de imágenes aquí
        framehsv = cv2.cvtColor(framebgr, cv2.COLOR_BGR2HSV)
        mbg = cv2.inRange(framehsv, (50, 70, 70), (90, 255, 255))
        mascarabg = cv2.merge((mbg,mbg,mbg))
        mascarabg = cv2.GaussianBlur(mascarabg, (7,7), 0)
        mascarafg = cv2.bitwise_not(mascarabg)
        fg =  cv2.bitwise_and(framebgr, mascarafg)
        bg =  cv2.bitwise_and(fondo, mascarabg)
        framebgr = cv2.bitwise_or(fg, bg)

        respuesta = None
        evento_voz.set()
        if not colaVoz.empty():
            respuesta = colaVoz.get()
            evento_voz.clear()
            # Imprimir texto en la pantalla
            if respuesta == team:
                texto = "Respuesta correcta!!"
                ubicacion = (10, 50)  # Posición del texto (x, y)
                cv2.putText(framebgr, texto, ubicacion, fuente, 2, color, 2)
            elif respuesta is not None:
                texto = f"Respuesta incorrecta: {respuesta}"
                ubicacion = (10, 50)
                cv2.putText(framebgr, texto, ubicacion, fuente, 2, color, 2)
            else:
                texto = "Que equipo es?"
                ubicacion = (10, 50)
                cv2.putText(framebgr, texto, ubicacion, fuente, 2, color, 2)

        fuente = cv2.FONT_HERSHEY_PLAIN
        color = (255, 255, 255)  # Blanco

        
        cv2.imshow('FutGuesser - Guess the football team.', framebgr)

        if cv2.waitKey(1) == ord(' '):
            break

    cap.release()
    cv2.destroyWindow('FutGuesser - Guess the football team.')


if __name__ == "__main__":
    main()

