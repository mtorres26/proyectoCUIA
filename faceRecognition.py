import os
import cv2
import face_recognition
import numpy as np
import json

def crearPerfil(nombre, archivo):
    with open(archivo, "r") as file:
        data = json.load(file)

    data[nombre] = {
        "nombre": nombre,
        "puntuacion" : 0,
    }

    # Guardar el diccionario actualizado en el archivo
    with open(archivo, "w") as file:
        json.dump(data, file, indent=4)

def crearCodificacion(framebgr):
    rgb_frame = cv2.cvtColor(framebgr, cv2.COLOR_BGR2RGB)
    face_encodings = face_recognition.face_encodings(rgb_frame)
    if len(face_encodings) == 0:
        print("No se ha detectado ninguna cara")
        return None
    
    return face_encodings


def reconocerCaras(carasConocidas, framebgr):
    rgb_frame = cv2.cvtColor(framebgr, cv2.COLOR_BGR2RGB)
    face_encodings = face_recognition.face_encodings(rgb_frame)
    if len(face_encodings) == 0:
        print("No se ha detectado ninguna cara")
        return None
    
    # Recorre usuarios y compara codificaciones de la cara
    for cara in carasConocidas.values():
        known_face_encodings = cara["codificacion"]
        coincidencia = face_recognition.compare_faces([known_face_encodings], face_encodings[0])
        if coincidencia is not None:
            return cara
        
    return None
