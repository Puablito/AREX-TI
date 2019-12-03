import os
import cv2
import numpy as np
import pytesseract
import math
# import ImagenProcesar
from AREXTI_PROCESOS import ImagenProcesar
from PIL import Image
import tempfile
import re


"""
    
"""


class Segmentador:

    def __init__(self, tesseract_cmd):
        self.__imagen = None
        self.ancho = 0
        self.alto = 0  # math.trunc(ancho * (16 / 9))
        self.areaMinima = (self.ancho * self.alto) * 0.6 / 100  # area minima que debe cumplir un contorno para ser considerado globo de chat
        self.gris = None
        self.imgEscalada = None
        self.canny = None
        self.difRango = 20          # PARAMETRO PARA MARCAR UMBRAL DE DIFERENCIA MAXIMA ENTRE IZQ Y DERECHA PARA CLASIFICAR GLOBO INDEFINIDO
        self.horizontal = False
        self.tesseract_cmd = tesseract_cmd
        self.extractor = None

    def get_imagen(self):
        return self.__imagen

    def set_imagen(self, imagen):
        self.__imagen = imagen

    def configurarImagen(self):
        imgPath = self.__imagen.get_path() + os.sep + self.__imagen.get_nombre()

        metadatos = self.__imagen.get_metadatos()

        imgOriginal = Image.open(imgPath)
        if 'Orientation' in metadatos:
            orientacion = int(metadatos['Orientation'])
            if orientacion == 3:
                imgOriginal = imgOriginal.rotate(180, expand=True)
            elif orientacion == 6:
                imgOriginal = imgOriginal.rotate(270, expand=True)
            elif orientacion == 8:
                imgOriginal = imgOriginal.rotate(90, expand=True)
        anchoOriginal = imgOriginal.width  # OBTENER ANCHO DE IMAGEN
        altoOriginal = imgOriginal.height  # OBTENER ALTO DE IMAGEN
        self.horizontal = anchoOriginal > altoOriginal
        if self.horizontal:
            if altoOriginal > 1080:
                altoEscalado = altoOriginal
            else:  # anchoOriginal > 700:
                altoEscalado = altoOriginal + 210  # 850 930
            r = altoEscalado / float(altoOriginal)
            anchoEscalado = int(anchoOriginal * r)
        else:
            if anchoOriginal > 1080:
                anchoEscalado = anchoOriginal
            else:  # anchoOriginal > 700:
                anchoEscalado = anchoOriginal + 210  # 850 930
            r = anchoEscalado / float(anchoOriginal)
            altoEscalado = int(altoOriginal * r)
        imgEscaladaO = imgOriginal.resize((anchoEscalado, altoEscalado), Image.ANTIALIAS)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_filename = temp_file.name
        imgEscaladaO.save(temp_filename, dpi=(300, 300))
        self.imgEscalada = cv2.imread(temp_filename)
        self.gris = cv2.cvtColor(self.imgEscalada, cv2.COLOR_BGR2GRAY)
        self.areaMinima = (anchoEscalado * altoEscalado) * 0.6 / 100
        self.ancho = anchoEscalado
        self.alto = altoEscalado

    def tratarImagen(self):
        # Aplicar suavizado Gaussiano
        gauss = cv2.GaussianBlur(self.gris, (5, 5), 0)
        # gauss = cv2.medianBlur(gris, 5)
        ret, tres = cv2.threshold(gauss, 10, 255, cv2.THRESH_TOZERO)  # +cv2.THRESH_OTSU)
        th = cv2.adaptiveThreshold(tres, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        kernel = np.ones((3, 3), np.uint8)
        erosion = cv2.erode(th, kernel, iterations=1)
        return erosion

    def obtenerBordes(self, erosion):
        canny = cv2.Canny(erosion, 0, 0)
        self.canny = canny
        # return canny

    def obtenerGlobos(self):
        # DEVUELVE LA LISTA CON LOS CONTORNOS RECONOCIDOS COMO GLOBOS DE CHAT
        globos = []
        # BUSCAMOS LOS CONTORNOS DE LA IMAGEN PROCESADA CON CANNY, ES DECIR LOS BORDES QUE FORMEN CONTORNOS
        (contornos, _) = cv2.findContours(self.canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # SE REDIBUJA SOBRE LA IMAGEN PARA COMPLETAR CONTORNOS SIN CERRAR
        cv2.drawContours(self.canny, contornos, -1, (255, 255, 255), 2)
        (contornos_optimizados, _) = cv2.findContours(self.canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contorno in reversed(contornos_optimizados):
             if cv2.contourArea(contorno) > self.areaMinima:
                globos.append(contorno)
        return globos

    def setearGlobos(self, contornos_finales):
        # Lectura de los contornos reconocidos como globos y se extraen de la imagen para detectar texto
        globos = []
        cabeceraDetalle = ImagenProcesar.ImagenDetalle()
        textoCabecera = self.extraerCabecera(self.canny)

        # SI LA CABECERA NO TIENE TEXTO O NO SE DETECTA NO SE GUARDA
        if textoCabecera.strip():
            cabeceraDetalle.set_tipoDetalle('CABECERA')
            cabeceraDetalle.set_texto(textoCabecera)
            globos.append(cabeceraDetalle)

        for i, contorno in enumerate(contornos_finales):
            mask = np.zeros_like(self.gris)  # tres
            cv2.drawContours(mask, contornos_finales, i, 255, -1)
            globo = np.zeros_like(self.gris)  # tres
            globo[mask == 255] = self.gris[mask == 255]  # tres
            globoColor = cv2.bitwise_and(self.imgEscalada, self.imgEscalada, mask=mask)
            # Cortar
            (x, y) = np.where(mask == 255)
            (topx, topy) = (np.min(x), np.min(y))
            (bottomx, bottomy) = (np.max(x), np.max(y))
            globo = globoColor[topx:bottomx + 1, topy:bottomy + 1]
            texto = self.extraerTextoImagen(globo)
            # SI EL GLOBO NO TIENE TEXTO O NO SE DETECTA NO SE GUARDA
            if not texto.strip():
                continue
            globoDetalle = ImagenProcesar.ImagenDetalle()

            leftmost = tuple(contorno[contorno[:, :, 0].argmin()][0])
            rightmost = tuple(contorno[contorno[:, :, 0].argmax()][0])
            rangoDerecha = self.ancho - rightmost[0]
            rangoIzquierda = leftmost[0]
            difRango = abs(rangoDerecha - rangoIzquierda)
            if difRango < self.difRango:
                globoDetalle.set_tipoDetalle('GLOBOINDEFINIDO')
            else:
                if rangoDerecha > rangoIzquierda:
                    globoDetalle.set_tipoDetalle('GLOBOIZQUIERDA')
                else:
                    globoDetalle.set_tipoDetalle('GLOBODERECHA')

            globoDetalle.set_texto(texto)
            globos.append(globoDetalle)

        globos2 = globos.copy()
        for globo in globos2:
            mails = self.obtenerMails(globo.get_texto())
            if mails:
                for mail in mails:
                    detalleMail = ImagenProcesar.ImagenDetalle()
                    detalleMail.set_tipoDetalle('MAIL')
                    detalleMail.set_texto(mail)
                    globos.append(detalleMail)
        return globos

    def extraerTextoImagen(self, img):
        if not self.extractor:
            self.extractor = ExtraccionTexto(self.tesseract_cmd)
        texto = self.extractor.extraerTexto(img)
        texto = texto.strip()
        texto = texto.replace('"', "")
        texto = texto.replace("'", "")
        texto = texto.replace("\n\n", "\n")
        texto = texto.replace("\n", " </br> ")
        return texto

    def extraerCabecera(self, canny):
        if self.horizontal:
            # PARAMETRO PARA LA FUNCION cv2.HoughLinesP 200
            minLargoLinea = math.trunc(self.alto * (125 / 3) / 100)
            maxEspacioLinea = math.trunc(self.alto * (125 / 3) / 100)  # PARAMETRO PARA LA FUNCION cv2.HoughLinesP 200
            # PARAMETRO PARA DEFINIR ALTO MAXIMO DE CABECERA EN CASO DE NO ENCONTRAR LINEAS POR DEBAJO DE ESE VALOR 260
            altoMaxCabecera = math.trunc(self.ancho * (128 / 8) / 100)
            altoMinCabecera = math.trunc(self.ancho * (
                    75 / 16) / 100)  # PARAMETRO PARA DEFINIR ALTO MINIMO DE CABECERA EN CASO DE ENCONTRAR LINEAS POR DEBAJO DE ESE VALOR 60
            lineaBarraInfo = math.trunc(self.ancho * (105 / 32) / 100)
            lineaCabecera = self.ancho
        else:
            minLargoLinea = math.trunc(self.ancho * (125 / 3) / 100)  # PARAMETRO PARA LA FUNCION cv2.HoughLinesP 200
            maxEspacioLinea = math.trunc(self.ancho * (125 / 3) / 100)  # PARAMETRO PARA LA FUNCION cv2.HoughLinesP 200
            altoMaxCabecera = math.trunc(self.alto * (
                        128 / 8) / 100)  # PARAMETRO PARA DEFINIR ALTO MAXIMO DE CABECERA EN CASO DE NO ENCONTRAR LINEAS POR DEBAJO DE ESE VALOR 260
            altoMinCabecera = math.trunc(self.alto * (
                        75 / 16) / 100)  # PARAMETRO PARA DEFINIR ALTO MINIMO DE CABECERA EN CASO DE ENCONTRAR LINEAS POR DEBAJO DE ESE VALOR 60
            lineaBarraInfo = math.trunc(self.alto * (105 / 32) / 100)
            lineaCabecera = self.alto

        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2))
        dilated = cv2.dilate(canny, kernel, iterations=1)
        lines = cv2.HoughLinesP(dilated, 1, np.pi / 180, 200, minLargoLinea, maxEspacioLinea)

        if lines is not None:
            for x in reversed(range(0, len(lines))):
                for x1, y1, x2, y2 in lines[x]:
                    # ANALIZO LAS LINEAS HORIZONTALES
                    if (x1 != x2) and (y1 == y2):
                        if altoMinCabecera < y1 < lineaCabecera:
                            lineaCabecera = y1

        if lineaCabecera > altoMaxCabecera:
            lineaCabecera = altoMaxCabecera

        cabecera = self.imgEscalada[lineaBarraInfo:lineaCabecera, 0:self.ancho]
        cabeceraTexto = self.extraerTextoImagen(cabecera)

        return cabeceraTexto

    def obtenerMails(self, texto):
        mails = re.findall(r'[\w\.-]+@[\w\.-]+', texto)
        return mails

    def segmentarChat(self):
        Is_OK = True
        try:
            self.configurarImagen()
            erosion = self.tratarImagen()
            self.obtenerBordes(erosion)
            contornos = self.obtenerGlobos()
            globos = self.setearGlobos(contornos)
        except Exception as e:
            Is_OK = False
            error = e

        if Is_OK:
            RtaSeg = ["OK", globos]
        else:
            RtaSeg = ["ERROR", error]

        return RtaSeg

    def segmentarMail(self):
        Is_OK = True
        try:
            detalles = []
            self.configurarImagen()
            texto = self.extraerTextoImagen(self.imgEscalada)
            detalle = ImagenProcesar.ImagenDetalle()
            detalle.set_tipoDetalle('TEXTO')
            detalle.set_texto(texto)
            detalles.append(detalle)
            mails = self.obtenerMails(texto)
            if mails:
                for mail in mails:
                    detalleMail = ImagenProcesar.ImagenDetalle()
                    detalleMail.set_tipoDetalle('MAIL')
                    detalleMail.set_texto(mail)
                    detalles.append(detalleMail)

        except Exception as e:
            Is_OK = False
            error = e

        if Is_OK:
            RtaSeg = ["OK", detalles]
        else:
            RtaSeg = ["ERROR", error]

        return RtaSeg

    def segmentarOtro(self):
        Is_OK = True
        try:
            detalles = []
            self.configurarImagen()
            texto = self.extraerTextoImagen(self.imgEscalada)
            detalle = ImagenProcesar.ImagenDetalle()
            detalle.set_tipoDetalle('TEXTO')
            detalle.set_texto(texto)
            detalles.append(detalle)
            mails = self.obtenerMails(texto)
            if mails:
                for mail in mails:
                    detalleMail = ImagenProcesar.ImagenDetalle()
                    detalleMail.set_tipoDetalle('MAIL')
                    detalleMail.set_texto(mail)
                    detalles.append(detalleMail)

        except Exception as e:
            Is_OK = False
            error = e

        if Is_OK:
            RtaSeg = ["OK", detalles]
        else:
            RtaSeg = ["ERROR", error]

        return RtaSeg

class ExtraccionTexto:
    def __init__(self, tesseract_cmd):
        # self.imagen = img
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd  # Cachear excepcion

    def extraerTexto(self, img):
        texto = pytesseract.image_to_string(img)
        return texto
