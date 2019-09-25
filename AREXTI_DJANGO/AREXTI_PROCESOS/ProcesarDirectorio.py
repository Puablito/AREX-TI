import os
import sys
import imghdr
import datetime
import time
import logging
from multiprocessing import Process, Queue
import RedesNeuronales
import Hashes
import Metadatos
import ImagenProcesar
import Segmentacion

# Se leen los parametros
'''
parser = argparse.ArgumentParser(description='Procesador de directorios')
parser.add_argument('-d', '--dir', required=True, type=str, help='Ingrese el path del directorio que se desea procesar')
#parser.add_argument('-a', '--hash', required=True, type=str, help='Ingrese el listado de hashes a aplicar')
args = parser.parse_args()

#print(args)
#listaHash = [args.hash] #'Casillas','Pique','Puyol' probar con un remplace de las comu¿illas
#print(listaHash)

rootDir = args.dir
'''
rootDir = r'C:\Users\Mariano-Dell\PycharmProjects\Imagenes\CapturasMarian'

# Insertar tabla de procesos, analizar paquete logging

# Listado de extensiones que se van a procesar
ListadoExtensiones = ["JPG", "JPEG", "PNG", "GIF", "TIFF"]

# Colas de trabajo multiproceso
ImagenesCola = Queue()
ImagenesGuardar_Cola = Queue()      # cola de las imagenes procesadas para guardar BD
imagenesNoTexto = Queue()          # cola con las imagenes no procesadas por no detectar texto en ellas

'''
 Se recorre el directorio que viene por parametro con sus subdirectorios en busqueda de archivos de imagenes, el
 listado de tipo de imagenes soportados está guardado en una varialbe "ListadoExtensiones".
 Se analizan todos los archivos y los que son de tipo imagen se guardan en una lista "ListaImagenes"
 
 Formato de cada elemento de la lista "ListaImagenes"
    elemento 0 = Ruta absoluta del archivo, Ej: F:/Proyects/Imagenes
    elemento 1 = Nombre del archivo, Ej: Twitter.jpg
    elemento 2 = Extensión del archivo, Ej: jpeg
'''
for dirName, subdirList, fileList in os.walk(rootDir):
    for fname in fileList:
        archivo = dirName + os.sep + fname
        # Identifico si "archivo" es imagen por el contenido y NO por la extensión
        if imghdr.what(archivo) is not None:
            ext = imghdr.what(archivo)
            if ext.upper() in ListadoExtensiones:
                ImagenesCola.put([dirName, fname, ext])


# Funcion que procesa la imagen recibida por paramentro
# noinspection PyBroadException
def procesar_imagen(procesoid, imagenes_cola, imagenes_guardar, imagenes_notexto):
    # instancio las RN
    try:
        rn_txt = RedesNeuronales.RedNeuronalTexto()
    except:
        logging.error('Error al instanciar la RN de Texto - ' + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

    try:
        rn_chat = RedesNeuronales.RedNeuronalChat()
    except:
        logging.error('Error al instanciar la RN de Chat - ' + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

    # try:
    #     # rn_mail = RedesNeuronales.RedNeuronalEmail()
    # except:
    #     logging.error('Error al instanciar la RN de Email - ' + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

    # instancio el segmentador
    try:
        segmentador = Segmentacion.Segmentador(720)
    except:
        logging.error('Error al instanciar el segmentador - ' + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

    while not imagenes_cola.empty():
        img_procesar = imagenes_cola.get()
        img_path = img_procesar[0]
        img_nombre = img_procesar[1]

        # print("--- Proceso {0} - imagen {1} ---".format(procesoid, img_nombre))
        imagen_procesada = ImagenProcesar.Imagen()
        imagen_procesada.set_nombre(img_procesar[1])
        imagen_procesada.set_extension(img_procesar[2])
        imagen_procesada.set_path(img_procesar[0])

        # Verifica si posee texto o no con la RN
        try:
            img_path = img_path + os.sep
            tiene_texto = rn_txt.imagen_tiene_texto(img_path, img_nombre)
        except:
            msgerror = 'Error en RN Texto, al intentar predecir la imagen (' + imagen_with_path + ") "
            logging.error(msgerror + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            continue

        if not tiene_texto:  # Si la imagen NO posee texto
            imagenes_notexto.put(img_path+img_nombre)
        else:  # Si la imagen posee texto

            imagen_with_path = img_path + img_nombre

            # Calcula Hashes
            try:
                listado_hashes = {"md5": "", "sha1": "", "sha256": ""}
                listado_hashes = Hashes.calcular_hashes(listado_hashes, imagen_with_path)
                imagen_procesada.set_hashes(listado_hashes)
            except:
                msgerror = 'Error al intentar calcular los hash de la imagen (' + imagen_with_path + ") "
                logging.error(msgerror + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                continue

            # Extrae metadatos
            try:
                listado_metadatos = Metadatos.metadata_extraer(imagen_with_path)
                imagen_procesada.set_metadatos(listado_metadatos)
            except:
                msgerror = 'Error al intentar calcular los metadatos de la imagen ('+imagen_with_path+") "
                logging.error(msgerror + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                continue

            # Verifica si es de chat o no con la RN
            try:
                img_path = img_path + os.sep
                es_chat = rn_chat.imagen_es_chat(img_path, img_nombre)
            except:
                msgerror = 'Error en RN Chat, al intentar predecir la imagen (' + imagen_with_path + ") "
                logging.error(msgerror + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                continue

            if es_chat:
                imagen_procesada.set_imagentipo("C")
                # Segmenta la imagen y extraer texto DE CHAT
            else:
                imagen_procesada.set_imagentipo("O")  # no chat
                '''
                # Verifica si es de mail o no con la RN
                
                img_path = img_path + os.sep
                es_mail = rn_mail.imagen_es_email(img_path, img_nombre)
    
                if es_mail:
                    pass  # Segmenta la imagen y extraer texto DE MAIL
                else:
                    pass  # Segmenta la imagen y extraer texto DE OTROS
                '''

            imagen_segmentada = segmentador.procesarImagen(imagen_procesada)  # LA CLASE IMAGEN PROCESADA INICIA EL PROCESO DE SEGMENTACION SEGUN EL TIPO DE IMAGEN SETEADO ARRIBA
            print("////////////////////////////////////////////////////////////////////////")
            print(imagen_segmentada.get_path())
            print("----------------------------------------")
            for detalle in imagen_segmentada.get_detalles():
                print("_____________________________________________________________________")
                print("Tipo globo: " + detalle.get_tipoGlobo())
                print(detalle.get_texto())
                print("_____________________________________________________________________")
            print("////////////////////////////////////////////////////////////////////////")
            # Guarda en BD
            imagenes_guardar.put(imagen_segmentada)


'''
 Inicio del procesamiento en paralelo
 
 1- Se crea un pool (piscina) de procesos activos (una lista)
 2- Se quita una imagen de la lista "ListaImagenes", se crea el proceso, se inicia y 
    se agrega a la piscina de procesos activos
 3- Mientras la piscina tenga procesos activos:
    A- Para cada proceso de la piscina revisamos si el proceso ha muerto
    B- Si ha muerto algun proceso lo recuperamos y lo sacamos de la piscina
    C- Mientras la piscina de procesos no esté llena y el listado de imagenes no esté vacio, 
       se realiza lo indicado en el paso 2
 4- El proceso finaliza cuando la piscina se encuentre vacia
'''

if __name__ == '__main__':
    print(str(ImagenesCola.qsize())+" Imagenes a procesar")
    print("Inicio la RN")
    TiempoInicial = datetime.datetime.now()

    procesos_paralelos = os.cpu_count()  # cantidad de procesos maximos a utilizar
    procesos_ejecucion = []              # cantidad de procesos en ejecución
    indiceProceso = 1

    # Creación de los procesos que procesaran las imagenes leidas
    while len(procesos_ejecucion) < procesos_paralelos and not ImagenesCola.empty():
        p = Process(name="Proceso {0}".format(indiceProceso),
                    target=procesar_imagen,
                    args=(indiceProceso, ImagenesCola, ImagenesGuardar_Cola, imagenesNoTexto,)
                    )
        p.start()
        procesos_ejecucion.append(p)
        print("Agrega: " + p.name)
        indiceProceso += 1

    # Mientras haya procesos en ejecución
    while procesos_ejecucion:

        # Revisa si los procesos han muerto
        for proceso in procesos_ejecucion:
            if not proceso.is_alive():
                print("Elimina: " + proceso.name)
                # Recuperamos el proceso y lo sacamos de la lista
                proceso.join()
                procesos_ejecucion.remove(proceso)
                del proceso

        # Guardado en archivo las imagenes que no se reconocieron con texto
        if not imagenesNoTexto.empty():
            with open("Imagenes_Sin_Texto.txt", "a") as archivo_notexto:
                while not imagenesNoTexto.empty():
                    archivo_notexto.write(imagenesNoTexto.get()+"\n")

        # Si hay imagenes ya procesadas para guardar las guarda
        # Realizar mas pruebas (si la cola "ImagenesGuardar_Cola" se llena los procesos no terminan)
        while not ImagenesGuardar_Cola.empty():
            img_guardar = ImagenesGuardar_Cola.get()
            print("Imagen: {0} - {1}".format(img_guardar.get_nombre(), img_guardar.get_imagentipo()))

        # Para no saturar el cpu, dormimos el ciclo durante 1 segundo
        time.sleep(1)

    print("WHILE: todos los procesos han terminado")

    TiempoFinal = datetime.datetime.now()
    print("Inicio: "+str(TiempoInicial))
    print("Fin:    "+str(TiempoFinal))
    print("Tiempo transcurrido: "+str(TiempoFinal - TiempoInicial))
