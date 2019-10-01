import os
import cv2
import numpy as np
import pytesseract
import math
import ImagenProcesar


class Segmentador:

    def __init__(self, ancho):
        self.imagen = None
        self.ancho = ancho
        self.alto = math.trunc(ancho * (16 / 9))
        self.areaMinima = (self.ancho * self.alto) * 0.6 / 100              # area minima que debe cumplir un contorno para ser considerado globo de chat
        self.gris = None
        self.difRango = 20          # PARAMETRO PARA MARCAR UMBRAL DE DIFERENCIA MAXIMA ENTRE IZQ Y DERECHA PARA CLASIFICAR GLOBO INDEFINIDO

        self.minLargoLinea = math.trunc(ancho * (250 / 9) / 100)         # PARAMETRO PARA LA FUNCION cv2.HoughLinesP 200
        self.maxEspacioLinea = math.trunc(ancho * (250 / 9) / 100)       # PARAMETRO PARA LA FUNCION cv2.HoughLinesP 200
        self.altoMaxCabecera = math.trunc(self.alto * (325 / 16) / 100)  # PARAMETRO PARA DEFINIR ALTO MAXIMO DE CABECERA EN CASO DE NO ENCONTRAR LINEAS POR DEBAJO DE ESE VALOR 260
        self.altoMinCabecera = math.trunc(self.alto * (75 / 16) / 100)   # PARAMETRO PARA DEFINIR ALTO MINIMO DE CABECERA EN CASO DE ENCONTRAR LINEAS POR DEBAJO DE ESE VALOR 60
        self.lineaBarraInfo = math.trunc(self.alto * (105 / 32) / 100)   # PARAMETRO PARA DEFINIR EL ALTO QUE SE VA A CORTAR DE LA CABECERA DE INFO DE FECHA RED ETC, DE LA CAPTURA 42

    def configurarImagen(self):
        imgPath = self.imagen.get_path() + os.sep + self.imagen.get_nombre()
        img = cv2.imread(imgPath)
        imgAncho = img.shape[1]  # ANCHO
        imgAlto = img.shape[0]   # ALTO
        if imgAlto > imgAncho:   # PARA VER SI ESTA LA IMAGEN ROTADA HORIZONTAL O VERTICAL
            dim = (self.ancho, self.alto)
        else:
            dim = (self.alto, self.ancho)
        img_escalada = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        self.gris = cv2.cvtColor(img_escalada, cv2.COLOR_BGR2GRAY)
        # cv2.imshow('imagenini ', self.gris)
        # cv2.waitKey(0)
        return self.gris

    def tratarImagen(self):
        # self.gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Aplicar suavizado Gaussiano
        gauss = cv2.GaussianBlur(self.gris, (5, 5), 0)
        # gauss = cv2.medianBlur(gris, 5)
        ret, tres = cv2.threshold(gauss, 10, 255, cv2.THRESH_TOZERO)  # +cv2.THRESH_OTSU)
        th = cv2.adaptiveThreshold(tres, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        kernel = np.ones((3, 3), np.uint8)
        erosion = cv2.erode(th, kernel, iterations=1)
        # cv2.imshow('erosion ', erosion)
        # cv2.waitKey(0)
        return erosion

    def obtenerBordes(self, erosion):
        canny = cv2.Canny(erosion, 0, 0)
        return canny

    def obtenerGlobos(self, canny):  # DEVUELVE LA LISTA CON LOS CONTORNOS RECONOCIDOS COMO GLOBOS DE CHAT
        globos = []
        # BUSCAMOS LOS CONTORNOS DE LA IMAGEN PROCESADA CON CANNY, ES DECIR LOS BORDES QUE FORMEN CONTORNOS
        (contornos, _) = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # RETR_EXTERNAL
        # SE REDIBUJA SOBRE LA IMAGEN PARA COMPLETAR CONTORNOS SIN CERRAR
        cv2.drawContours(canny, contornos, -1, (255, 255, 255), 2)
        (contornos_optimizados, _) = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # i = 0
        # cv2.imshow('cannyContorno ', canny)
        # cv2.waitKey(0)
        # contornos_finales = []
        for contorno in reversed(contornos_optimizados):
            # print('contorno: '+ str(i)+' Area: '+ str(cv2.contourArea(contorno)))
            if cv2.contourArea(contorno) > self.areaMinima:  # contorno.size>200 and 35000
                # globoDetalle = self.setearGlobos(contorno)
                globos.append(contorno)
                # i = i + 1
        cv2.drawContours(self.gris, globos, -1, (0, 0, 255), 2)
        imgS = cv2.resize(self.gris, (540, 960))
        cv2.imshow('cannyContorno ', imgS)
        cv2.waitKey(0)
        return globos

    def setearGlobos(self, contornos_finales):  # SE LEE LA LISA DE CONTORNOS RECONOCIDOS COMO GLOBOS Y SE EXTAEN DE LA IMAGEN PARA DETECTAR TEXTO Y SE SETEAN SUS PROPIEDADES
        # j = 0
        globos = []
        for i, contorno in enumerate(contornos_finales):
            mask = np.zeros_like(self.gris)  # tres
            cv2.drawContours(mask, contornos_finales, i, 255, -1)
            globo = np.zeros_like(self.gris)  # tres
            globo[mask == 255] = self.gris[mask == 255]  # tres

            # Cortar
            (x, y) = np.where(mask == 255)
            (topx, topy) = (np.min(x), np.min(y))
            (bottomx, bottomy) = (np.max(x), np.max(y))
            globo = globo[topx:bottomx + 1, topy:bottomy + 1]
            globoDetalle = ImagenProcesar.ImagenDetalle()

            leftmost = tuple(contorno[contorno[:, :, 0].argmin()][0])
            rightmost = tuple(contorno[contorno[:, :, 0].argmax()][0])
            rangoDerecha = self.ancho - rightmost[0]
            rangoIzquierda = leftmost[0]
            difRango = abs(rangoDerecha - rangoIzquierda)
            if difRango < self.difRango:
                globoDetalle.set_tipoGlobo('U')
            else:
                if rangoDerecha > rangoIzquierda:
                    globoDetalle.set_tipoGlobo('I')
                else:
                    globoDetalle.set_tipoGlobo('D')

            texto = self.extraerTextoImagen(globo)
            globoDetalle.set_texto(texto)
            globos.append(globoDetalle)
            print("GLOBO " + str(i))
            print(texto)
            # cv2.imshow('Output ' + str(j), globo)
            # j = j + 1
            # cv2.imshow('Output ', globo)
            # cv2.waitKey(0)
        return globos

    def extraerTextoImagen(self, img):
        extractor = ExtraccionTexto(img)
        texto = extractor.extraerTexto()
        return texto

    def extraerCabecera(self, canny):
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2))
        dilated = cv2.dilate(canny, kernel, iterations=1)
        # cv2.imshow("hough", dilated)
        # cv2.waitKey(0)
        lines = cv2.HoughLinesP(dilated, 1, np.pi / 180, 200, self.minLargoLinea, self.maxEspacioLinea)
        lineaCabecera = self.alto
        for x in reversed(range(0, len(lines))):
            for x1, y1, x2, y2 in lines[x]:
                # ANALIZO LAS LINEAS HORIZONTALES
                if (x1 != x2) and (y1 == y2):
                    if self.altoMinCabecera < y1 < lineaCabecera:
                        lineaCabecera = y1

        if lineaCabecera > self.altoMaxCabecera:
            lineaCabecera = self.altoMaxCabecera
        # imgS = cv2.resize(original, (540, 960))
        # cv2.imshow("hough", imgS)
        cabecera = self.gris[self.lineaBarraInfo:lineaCabecera, 0:self.ancho]
        cabeceraTexto = self.extraerTextoImagen(cabecera)
        print("CABECERA: ******************************************")
        print(cabeceraTexto)
        print("FIN CABECERA: ******************************************")
        # cv2.imshow("cabecera", cabecera)
        # cv2.waitKey(0)
        return cabeceraTexto

    def segmentarChat(self):
        self.configurarImagen()
        erosion = self.tratarImagen()
        canny = self.obtenerBordes(erosion)
        textoCabecera = self.extraerCabecera(canny)
        # FALTA VER DONDE SETEAR EL TEXTO DE CABECERA, ATRIBUTO EN CLASE IMAGEN?
        contornos = self.obtenerGlobos(canny)
        globos = self.setearGlobos(contornos)
        return globos

    def segmentarMail(self):
        detalles = []
        img = self.configurarImagen
        texto = self.extraerTextoImagen(img)
        detalle = ImagenProcesar.ImagenDetalle()
        detalle.set_texto(texto)
        detalles.append(detalle)
        return detalles

    def segmentarOtro(self):
        detalles = []
        img = self.configurarImagen
        texto = self.extraerTextoImagen(img)
        detalle = ImagenProcesar.ImagenDetalle()
        detalle.set_texto(texto)
        detalles.append(detalle)
        return detalles

    def procesarImagen(self, imagen):
        tipo = imagen.get_imagentipo()
        self.imagen = imagen
        if tipo == 'C':
            imagen.set_detalles(self.segmentarChat())
        else:
            if tipo == 'M':
                imagen.set_detalles(self.segmentarMail())
            else:
                imagen.set_detalles(self.segmentarOtro())
        return imagen


class ExtraccionTexto:
    imagen = None
    # HACER CONFIGURABLE LOS PATHS. HACER SINGLETON
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
    tessdata_dir_config = r'--tessdata-dir "C:\Program Files(x86)\Tesseract-OCR\tessdata"'

    def __init__(self, img):
        self.imagen = img

    def extraerTexto(self):
        texto = pytesseract.image_to_string(self.imagen)
        return texto
