import cv2
import face_recognition
import pyaudio
import sounddevice
import speech_recognition as sr
import random
import threading
import queue
from faceRecognition import reconocerCaras, crearCodificacion
import json
import numpy as np

# Funcion para cargar un mapa en formato JSON
def cargar_json(filename):
    # Cargar el archivo JSON con el mapa 
    with open(filename, "r") as file:
        try: 
            return json.load(file)
        except json.JSONDecodeError:
            print("El archivo JSON esta vacio")
            return {}

# Funcion para añadir un usuario al JSON
def add_user(name, codificacion, file_path):
    data = cargar_json(file_path)

    data[name] = {
        "nombre": name,
        "codificacion": codificacion[0].tolist(),  
        "puntuacion": 0,
    }

    # Guardar el diccionario actualizado en el archivo
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


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

def sumarPuntuacion(nombre, archivo):
    with open(archivo, "r") as file:
        data = json.load(file)

    data[nombre]["puntuacion"] += 1

    # Guardar el diccionario actualizado en el archivo
    with open(archivo, "w") as file:
        json.dump(data, file, indent=4)


# Función que devuelve un equipo de fútbol aleatorio
def randomTeam():
    teams = ["Bayern Munich", "Betis", "Granada", "Rayo Vallecano", "Levante"]
    return teams[random.randint(0, len(teams) - 1)]


def main():
    # Generacion de equipo aleatorio
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

    # Inicialización de colas y listas
    usuarios = cargar_json("bbdd.json")    # Cargar los usuarios del archivo JSON
    colaVoz = queue.Queue()  # Cola para almacenar lo que se dice por el microfono

    # Inicializar threads de voz y de cara
    evento_voz = threading.Event()
    hilo_datos = threading.Thread(target=escuchar, daemon=True, args=(colaVoz, evento_voz))
    hilo_datos.start()

    # Inicializacion de variables para la respuesta por pantalla
    respuesta = None
    fuente = cv2.FONT_HERSHEY_PLAIN
    color = (0, 0, 0)  # Negro
    ubicacion = (10, 50)  # Posición del texto (x, y)
    texto = "Que equipo es?"

    inicioSesion = False

    usuarios = cargar_json("bbdd.json")

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

        # Si no esta iniciada la sesion
        if not inicioSesion:
            # Recargar JSON por si se crea un nuevo perfil
            usuarios = cargar_json("bbdd.json")
            # Iniciar sesión
            usuario = reconocerCaras(usuarios, framebgr)
            
            if usuario:
                inicioSesion = True
                # Cargar sesion si se ha reconocido la cara
                print(f"Bienvenido, {usuario['nombre']}") 
            else:
                # Crear perfil de usuario 
                print("No se ha reconocido tu cara. Como te llamas?")

                # Preguntar al usuario su nombre mediante voz
                nombre = None
                evento_voz.set() # Activar la escucha del microfono
                while nombre is None:
                    cv2.imshow('FutGuesser - Guess the football team.', framebgr)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        exit(0)
                    ret, framebgr = cap.read()

                    if not colaVoz.empty():
                        nombre = colaVoz.get()
                        evento_voz.clear() # Desactivar la escucha del microfono
                        print("Se va a escanear tu cara, " + nombre + ". Por favor, mira al frente y no te muevas")

                        # Tomar frames para crear la codificación de la cara durante 3 segundos
                        codificacion = crearCodificacion(framebgr)
                        add_user(nombre, codificacion, "bbdd.json")

                        # Se vuelve a cargar JSON para actualizar la lista de usuarios
                        usuarios = cargar_json("bbdd.json")
                        usuario = reconocerCaras(usuarios, framebgr)               
                        print("Usuario registrado. Bienvenido, " + nombre + ".")
                    
                texto = "Bienvenido, " + nombre + ". Tu perfil ha sido creado"
                cv2.putText(framebgr, texto, ubicacion, fuente, 2, color, 2)
                cv2.imshow('FutGuesser - Guess the football team.', framebgr)
                inicioSesion = True
                        
        # Si la codificacion de la cara ya esta almacenada en el JSON
        else:
            respuesta = None
            evento_voz.set()
            if not colaVoz.empty():
                respuesta = colaVoz.get()
                evento_voz.clear()
                # Imprimir texto en la pantalla
                if respuesta is not None:
                    if team in respuesta:
                        usuarios = cargar_json("bbdd.json") 
                        sumarPuntuacion(usuario["nombre"], "bbdd.json")
                        usuarios = cargar_json("bbdd.json") 
                        punt = usuarios[usuario["nombre"]]["puntuacion"]
                        texto = f"Respuesta correcta!! Puntuacion: {punt}"
                    elif respuesta is not None:
                        texto = f"Respuesta incorrecta: {respuesta}"
                    else:
                        texto = "Que equipo es?"
        
        cv2.putText(framebgr, texto, ubicacion, fuente, 2, color, 2)
        
        cv2.imshow('FutGuesser - Guess the football team.', framebgr)

        if cv2.waitKey(1) == ord(' '):
            break

    cap.release()
    cv2.destroyWindow('FutGuesser - Guess the football team.')


if __name__ == "__main__":
    main()

