import cv2
import numpy as np
from matplotlib import pyplot as plt
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
tessdata_dir_config = r'--tessdata-dir "C:\Program Files(x86)\Tesseract-OCR\tessdata"'

# Cargamos la imagen
original = cv2.imread(r'C:\Program Files (x86)\Tesseract-OCR\tessdata\Capturas\Recortadas\AndroidTuenti.jpeg')
# texto1 = pytesseract.image_to_string(original)
# print(texto1)
# Convertimos a escala de grises
gris = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
# Aplicar suavizado Gaussiano
# gauss = cv2.GaussianBlur(gris, (5, 5), 0)

# SE APLICA LA FUNCION TRESHOLD PARA DETECTAR MEJOR LOS BORDES DE LOS GLOBOS.
ret,tres = cv2.threshold(gris,243,255,cv2.THRESH_BINARY) # 235 226 ios  238  236

# Detectamos los bordes con Canny
canny = cv2.Canny(tres, 0, 0) #
#
cv2.namedWindow("canny")#, cv2.WINDOW_NORMAL)
cv2.imshow("canny", tres)
# cv2.imwrite("captura_canny.jpg",tres)

# BUSCAMOS LOS CONTORNOS DE LA IMAGEN PROCESADA CON CANNY, ES DECIR LOS BORDES QUE FORMEN CONTORNOS
(contornos,_) = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # RETR_EXTERNAL
idx = 0
# cont=cv2.contourArea(contornos[43])
cv2.drawContours(canny,contornos,-1,(255,255,255), 2)
(contornos_optimizados,_) = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.imwrite("captura_canny.jpg",canny)
# cv2.namedWindow("canny2")
# cv2.imshow("canny", canny)

i = 0
contornos_finales = []
for contorno in contornos_optimizados:
    # print('contorno: '+ str(i)+' Area: '+ str(cv2.contourArea(contorno)))
    if cv2.contourArea(contorno) > 1000: #contorno.size>200 and 35000
        contornos_finales.append(contorno)
        print(str(i)+'  - '+str(contorno.size)+' Alto: '+str(contorno.shape[0])+' Area: '+str(cv2.contourArea(contorno)))
        # print('Area: '+str(cv2.contourArea(contorno)))
        i = i+1

#  CICLO PARA RECORRER LOS CONTORNOS DE POSIBLES GLOBOS DETECTADOS Y DETECTAR EL TEXTO EN CADA UNO
j=0
for contorno in contornos_finales:
    mask = np.zeros_like(gris) # tres
    cv2.drawContours(mask, contornos_finales, j, 255, -1)
    out = np.zeros_like(gris) # tres
    # cv2.imshow("mask", mask)
    out[mask == 255] = gris[mask == 255] # tres

    # Now crop
    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    out = out[topx:bottomx + 1, topy:bottomy + 1]
    print('Globo: '+ str(j))
    texto = pytesseract.image_to_string(out)
    print(texto)
    cv2.imshow('Output ' + str(j), out)

    # ret, out2 = cv2.threshold(out, 226, 255, cv2.THRESH_BINARY) # 222 ios
    # texto = pytesseract.image_to_string(out2)
    # print(texto)
    # cv2.imshow('Output2 ' + str(j), out2)
    #
    # out3 = cv2.medianBlur(out2, 3)
    # texto = pytesseract.image_to_string(out3)
    # print(texto)
    # cv2.imshow('Output3 ' + str(j), out3)
    j = j+1
# CONVIENE PRIMERO OBTENER LOS GLOBOS DE LA IMAGEN EN GRIS Y DESPUES MEJORARLOS CON TRESHOLD, PORQUE SI AGARRO DE UNA LA IMAGEN DEL TRESHOLD PUEDE PASAR
# COMO EN EL CASO DE TUENTI QUE SE DETECTARON LOS GLOBOS PERO QUEDARON TODOS NEGROS POR EL UMBRAL UTILIZADO, ENTONCES LUEGO NO PUEDE LEER EL OCR.
# cv2.namedWindow('contornos', cv2.WINDOW_NORMAL)
# cv2.drawContours(canny,contornos,-1,(255,255,255), 2)
# cv2.imwrite("original_contornos.jpg",canny)
# cv2.imshow("contornos", canny)
# ret,tres=cv2.threshold(gris,226,255,cv2.THRESH_BINARY)
cv2.waitKey(0)