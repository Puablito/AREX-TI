# Modulo de Redes Neuronales
import cv2
import numpy as np
import os
from tensorflow.python.keras.preprocessing.image import img_to_array
from tensorflow.python.keras.models import load_model


class RedNeuronalTexto:
    __instancetexto = None

    def __new__(cls):
        if RedNeuronalTexto.__instancetexto is None:
            RedNeuronalTexto.__instancetexto = object.__new__(cls)
        return RedNeuronalTexto.__instancetexto

    def __init__(self):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'RN_MODELOS')
        modelo = path + os.sep + "RNTexto.h5"
        try:
            self.cnnTexto = load_model(modelo)
        except:
            resultado = ["ERROR", "No se pudo cargar la RN de Texto, path: {0}".format(modelo)]
            return resultado
        self.targetSize = (320, 320)

    # Indica si una imagen posee texto o no
    def imagen_tiene_texto(self, imagen_path, imagen_nombre):
        resultado = False
        archivononmbre = imagen_path + imagen_nombre
        imagen = cv2.imread(archivononmbre, cv2.IMREAD_GRAYSCALE)
        if imagen is None:  # always check for None
            resultado = ["ERROR", "No se pudo cargar la imagen {0}".format(archivononmbre)]
            return resultado
        else:
            # Se orocesa la imagen antes de realizar la predicción
            imagen = cv2.resize(imagen, self.targetSize, interpolation=cv2.INTER_AREA)
            imagen = img_to_array(imagen)
            imagen = np.expand_dims(imagen, axis=0)  # agrega una dimensión al array
            imagen = np.array(imagen)                # Transforma la imagen en un arreglo de numpy
            imagen = imagen.astype('float32') / 255  # se pasan a valores entre 0 y 1

            # Se realizo la predicción
            array = self.cnnTexto.predict(imagen, verbose=0)
            result = array[0]  # Me quedo con el primer elemento de la matriz para usarlo como vector
            answer = np.argmax(result)

            if answer == 0:
                resultado = ["OK", True]
            elif answer == 1:
                resultado = ["OK", False]

            return resultado


class RedNeuronalChat:
    __instancechat = None

    def __new__(cls):
        if RedNeuronalChat.__instancechat is None:
            RedNeuronalChat.__instancechat = object.__new__(cls)
        return RedNeuronalChat.__instancechat

    def __init__(self):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'RN_MODELOS')
        modelo = path + os.sep + "RNChat.h5"
        try:
            self.cnnChat = load_model(modelo)
        except:
            resultado = ["ERROR", "No se pudo cargar la RN de Chat, path: {0}".format(modelo)]
            return resultado
        self.targetSize = (350, 260)

    def imagen_es_chat(self, imagen_path, imagen_nombre):
        resultado = False
        archivononmbre = imagen_path + imagen_nombre
        imagen = cv2.imread(archivononmbre, cv2.IMREAD_GRAYSCALE)
        if imagen is None:  # always check for None
            resultado = ["ERROR", "No se pudo cargar la imagen {0}".format(archivononmbre)]
            return resultado
        else:
            # Se orocesa la imagen antes de realizar la predicción
            imagen = cv2.resize(imagen, self.targetSize, interpolation=cv2.INTER_AREA)
            imagen = img_to_array(imagen)
            imagen = np.expand_dims(imagen, axis=0)  # agrega una dimensión al array
            imagen = np.array(imagen)                # Transforma la imagen en un arreglo de numpy
            imagen = imagen.astype('float32') / 255  # se pasan a valores entre 0 y 1

            # Se realizo la predicción
            array = self.cnnChat.predict(imagen, verbose=0)
            result = array[0]  # Me quedo con el primer elemento de la matriz para usarlo como vector
            answer = np.argmax(result)

            if answer == 0:
                resultado = ["OK", True]
            elif answer == 1:
                resultado = ["OK", False]

            return resultado


class RedNeuronalEmail:
    __instancemail = None

    def __new__(cls):
        if RedNeuronalEmail.__instancemail is None:
            RedNeuronalEmail.__instancemail = object.__new__(cls)
        return RedNeuronalEmail.__instancemail

    def __init__(self):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'RN_MODELOS')
        modelo = path + os.sep + "RNMail.h5"
        try:
            self.cnn = load_model(modelo)
        except:
            resultado = ["ERROR", "No se pudo cargar la RN de Mail, path: {0}".format(modelo)]
            return resultado
        self.targetSize = (350, 260)

    def imagen_es_email(self, imagen_path, imagen_nombre):
        resultado = False
        archivononmbre = imagen_path + imagen_nombre
        imagen = cv2.imread(archivononmbre, cv2.IMREAD_GRAYSCALE)
        if imagen is None:  # always check for None
            resultado = ["ERROR", "No se pudo cargar la imagen {0}".format(archivononmbre)]
            return resultado
        else:
            # Se orocesa la imagen antes de realizar la predicción
            imagen = cv2.resize(imagen, self.targetSize, interpolation=cv2.INTER_AREA)
            imagen = img_to_array(imagen)
            imagen = np.expand_dims(imagen, axis=0)  # agrega una dimensión al array
            imagen = np.array(imagen)                # Transforma la imagen en un arreglo de numpy
            imagen = imagen.astype('float32') / 255  # se pasan a valores entre 0 y 1

            # Se realizo la predicción
            array = self.cnn.predict(imagen, verbose=0)
            result = array[0]  # Me quedo con el primer elemento de la matriz para usarlo como vector
            answer = np.argmax(result)

            if answer == 0:
                resultado = ["OK", True]
            elif answer == 1:
                resultado = ["OK", False]

            return resultado
