import cv2
import face_recognition
import numpy as np
import speech_recognition as sr
import random

# Función que devuelve la transcripción de lo que se dice en el micrófono
def escuchar():
    r = sr.Recognizer()
    transcripcion = None
    while transcripcion is None:
        with sr.Microphone() as source:
            audio = r.listen(source, phrase_time_limit=10)
        try:
            transcripcion = r.recognize_google(audio, language='es-ES')
        except sr.UnknownValueError:
            transcripcion = None
        except sr.RequestError:
            transcripcion = None
        if transcripcion is not None:
            print("Google Speech Recognition thinks you said " + transcripcion)

    return transcripcion
    

# Función que devuelve un equipo de fútbol aleatorio
def randomTeam():
    teams = ["Bayern Munich", "Betis"]
    return teams[random.randint(0, 1)]


# Función que realiza el croma con la equipación de un equipo de fútbol
def croma(team):
    equipment = cv2.imread(f"./img/{team}.png")

    cv2.namedWindow("FutGuesser - Guess the football team.")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Couldn't open the camera. Exiting...")
        exit()

    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fondo = cv2.resize(equipment, (ancho,alto))

    while cap.isOpened():
        ret, framebgr = cap.read()

        if not ret:
            print("Couldn't read the frame. Exiting...")
            break

        # Procesado de imágenes aquí
        framehsv = cv2.cvtColor(framebgr, cv2.COLOR_BGR2HSV)
        mbg = cv2.inRange( framehsv, (50, 70, 70), (90, 255, 255))
        mascarabg = cv2.merge((mbg,mbg,mbg))
        mascarabg = cv2.GaussianBlur(mascarabg, (7,7), 0)
        mascarafg = cv2.bitwise_not(mascarabg)
        fg =  cv2.bitwise_and(framebgr, mascarafg)
        bg =  cv2.bitwise_and(fondo, mascarabg)
        framebgr = cv2.bitwise_or(fg, bg)

        # Imprimir texto en la pantalla
        fuente = cv2.FONT_HERSHEY_PLAIN
        color = (255, 255, 255)  # Blanco
        texto = "Imprimiendo palabras..."  
        ubicacion = (10, 50)  # Posición del texto (x, y)
        cv2.putText(framebgr, texto, ubicacion, fuente, 1, color, 2)
        
        cv2.imshow('FutGuesser - Guess the football team.', framebgr)

        if cv2.waitKey(1) == ord(' ') or cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyWindow('FutGuesser - Guess the football team.')

    


def main():
    team = randomTeam()
    croma(team)
    guess = escuchar()
    if(guess == team):
        print("¡Has acertado!")
    else: 
        print("¡Has fallado! La respuesta correcta era: " + team)



if __name__ == "__main__":
    main()

