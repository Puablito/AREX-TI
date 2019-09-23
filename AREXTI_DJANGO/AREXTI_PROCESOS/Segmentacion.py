import cv2
import numpy as np
import pytesseract
import math
import ImagenProcesar


class Segmentacion:

    def __init__(self, ancho):
        # self.imagen = imagen
        # self.tipo = tipo
        self.ancho = ancho
        self.alto = math.trunc(ancho * 1.7777777777777777777777777777778)
        self.areaMinima = (self.ancho * self.alto) * 0.6 / 100              # area minima que debe cumplir un contorno para ser considerado globo de chat
        self.puntoIzquierda = self.ancho * 4.7 / 100                        # punto para considerar si es globo de izq o derecha
        self.gris = None

    def configurarImagen(self):
        img = cv2.imread(self.imagen.get_path)
        imgAncho = img.shape[1] # ANCHO
        imgAlto = img.shape[0] # ALTO
        if imgAlto > imgAncho: # PARA VER SI ESTA LA IMAGEN ROTADA HORIZONTAL O VERTICAL
            dim = (self.ancho, self.alto)
        else:
            dim = (self.alto, self.ancho)
        img_escalada = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        self.gris = cv2.cvtColor(img_escalada, cv2.COLOR_BGR2GRAY)
        return img_escalada

    def tratarImagen(self, img):
        # self.gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Aplicar suavizado Gaussiano
        gauss = cv2.GaussianBlur(self.gris, (5, 5), 0)
        # gauss = cv2.medianBlur(gris, 5)
        ret, tres = cv2.threshold(gauss, 10, 255, cv2.THRESH_TOZERO)  # +cv2.THRESH_OTSU)
        th = cv2.adaptiveThreshold(tres, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        kernel = np.ones((3, 3), np.uint8)
        erosion = cv2.erode(th, kernel, iterations=1)
        return erosion

    def obtenerGlobos(self, img):  # DEVUELVE LA LISTA CON LOS DETALLES DE LOS GLOBOS
        globos = []
        # Detectamos los bordes con Canny
        canny = cv2.Canny(img, 0, 0)
        # BUSCAMOS LOS CONTORNOS DE LA IMAGEN PROCESADA CON CANNY, ES DECIR LOS BORDES QUE FORMEN CONTORNOS
        (contornos, _) = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # RETR_EXTERNAL
        # SE REDIBUJA SOBRE LA IMAGEN PARA COMPLETAR CONTORNOS SIN CERRAR
        cv2.drawContours(canny, contornos, -1, (255, 255, 255), 2)
        (contornos_optimizados, _) = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        i = 0
        contornos_finales = []
        for contorno in reversed(contornos_optimizados):
            # print('contorno: '+ str(i)+' Area: '+ str(cv2.contourArea(contorno)))
            if cv2.contourArea(contorno) > self.areaMinima:  # contorno.size>200 and 35000
                globoDetalle = self.setearGlobos(contorno)
                globos.append(globoDetalle)
                i = i + 1
        return globos

    def setearGlobos(self, contorno):
        # j = 0
        # globos = []
        # for contorno in reversed(contornos_finales):
        mask = np.zeros_like(self.gris)  # tres
        cv2.drawContours(mask, contorno, -1, 255, -1)
        globo = np.zeros_like(self.gris)  # tres
        globo[mask == 255] = self.gris[mask == 255]  # tres

        # Cortar
        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        globo = globo[topx:bottomx + 1, topy:bottomy + 1]
        globoDetalle = ImagenProcesar.ImagenDetalle()

        leftmost = tuple(contorno[contorno[:, :, 0].argmin()][0])
        if leftmost[0] < self.puntoIzquierda:
            globoDetalle.tipoGlobo = 'I'
        else:
            globoDetalle.tipoGlobo = 'D'

        texto = self.extraerTextoImagen(globo)
        globoDetalle.texto = texto
        # globos.append(globoDetalle)
        # print(texto)
        # cv2.imshow('Output ' + str(j), globo)
        # j = j + 1
        return globoDetalle

    def extraerTextoImagen(self, img):
        extractor = ExtraccionTexto(img)
        texto = extractor.extraerTexto()
        return texto

    def segmentarChat(self):
        img = self.configurarImagen()
        imgTratada = self.tratarImagen(img)
        globos = self.obtenerGlobos(imgTratada)
        # globos = self.extraerGlobos(contornos)
        return globos

    def segmentarMail(self):
        detalles = []
        img = self.configurarImagen
        texto = self.extraerTextoImagen(img)
        detalle = ImagenProcesar.ImagenDetalle(self.imagen.id)
        detalle.texto = texto
        detalles.append(detalle)
        return detalles


    def segmentarOtro(self):
        detalles = []
        img = self.configurarImagen
        texto = self.extraerTextoImagen(img)
        detalle = ImagenProcesar.ImagenDetalle(self.imagen.id)
        detalle.texto = texto
        detalles.append(detalle)
        return detalles

    def procesarImagen(self, imagen):
        if imagen.get_imagentipo == 'C':
            imagen.set_detalles = self.segmentarChat()
        else:
            if imagen.get_imagentipo == 'M':
                imagen.set_detalles = self.segmentarMail()
            else:
                imagen.set_detalles = self.segmentarOtro()


class ExtraccionTexto:
    imagen = None

    def __init__(self, img):
        self.imagen = img

    def extraerTexto(self):
        texto = pytesseract.image_to_string(self.imagen)
        return texto
