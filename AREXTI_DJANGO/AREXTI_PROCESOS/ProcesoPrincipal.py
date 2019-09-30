import os
import imghdr
import datetime
import time
import argparse
import json
import ProcesadorImagen
from multiprocessing import Process, Queue

# llamada de ejemplo (DESACTIVADAS)
# Notebook Pablo
# ProcesoPrincipal.py -t d -p 1 -a {\"md5\":\"\",\"sha1\":\"\",\"sha256\":\"\"} -d D:\PythonProyects\SegmentacionIMG\Imagenes

# Notebook Marian
# ProcesoPrincipal.py -t d -p 1 -a {\"md5\":\"\",\"sha1\":\"\",\"sha256\":\"\"} -d r'C:\Users\Mariano-Dell\PycharmProjects\Imagenes\CapturasMarian

if __name__ == '__main__':
    '''
    # Se leen los parametros
    parser = argparse.ArgumentParser(description='Proceso principal')
    parser.add_argument('-d', '--dir', required=True, type=str,
                        help='Path del directorio que se desea procesar')
    parser.add_argument('-a', '--hash', required=True, type=str,
                        help='Listado de hashes a aplicar')
    parser.add_argument('-t', '--tipo', required=True, type=str,
                        help='Tipo de proceso a realizar (d = directorio a = archivos)')
    parser.add_argument('-p', '--pericia', required=True, type=str,
                        help='Número de pericia')
    args = parser.parse_args()

    #listaHash = {\"md5\":\"\",\"sha1\":\"\",\"sha256\":\"\"} asi tiene que venir
    print("Pericia {0} Tipo {1} hashes {2}".format(args.pericia, args.tipo, args.hash))
    print("Directorio {0}".format(args.dir))
    pericia = args.pericia
    procesotipo = args.tipo
    listaHash = json.loads(args.hash)
    rootDir = args.dir
'''
###################### Parametros hardcodeados ######################################
    # rootDir = r'C:\Users\Mariano-Dell\PycharmProjects\Imagenes\CapturasMarian'
    rootDir = 'D:\PythonProyects\SegmentacionIMG\Imagenes'
    listaHash = {"md5": "", "sha1": "", "sha256": ""}

    # Insertar tabla de procesos, analizar paquete logging

    # Listado de extensiones que se van a procesar
    ListadoExtensiones = ["JPG", "JPEG", "PNG", "GIF", "TIFF"]

    # Colas de trabajo multiproceso
    ImagenesCola = Queue()             # cola de imagenes a procesar
    ImagenesGuardar_Cola = Queue()     # cola de imagenes procesadas para guardar BD
    imagenesNoTexto = Queue()          # cola de imagenes no procesadas por no detectar texto en ellas

    '''
     Se recorre el directorio que viene por parametro con sus subdirectorios en busqueda de archivos de imagenes, el
     listado de tipo de imagenes soportados está guardado en una varialbe "ListadoExtensiones".
     Se analizan todos los archivos y los que son de tipo imagen se guardan en una cola "ImagenesCola"
     
     Formato de cada elemento de la cola "ImagenesCola"
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

    '''
     Inicio del procesamiento en paralelo
     
     1- Se crea un pool de procesos activos "procesos_ejecucion"
     2- Se crean los procesos, se inician y se agrega a "procesos_ejecucion"
     3- Mientras "procesos_ejecucion" tenga procesos activos:
        A- Para cada proceso revisamos si el proceso sigue vivo
        B- Si ha muerto algun proceso lo recuperamos, le quitamos los recursos y lo sacamos de "procesos_ejecucion"
        
# CAMBIAR EL PUNTO c YA QUE CAMBIO LA LOGICA       
        C- Mientras la piscina de procesos no esté llena y el listado de imagenes no esté vacio, 
           se realiza lo indicado en el paso 2
     4- El proceso finaliza cuando "procesos_ejecucion" se encuentre vacio
    '''
    print(str(ImagenesCola.qsize())+" Imagenes a procesar")
    TiempoInicial = datetime.datetime.now()

    procesos_paralelos = os.cpu_count()  # cantidad de procesos maximos a utilizar
    procesos_ejecucion = []              # cantidad de procesos en ejecución
    indiceProceso = 1

    # Creación de los procesos que procesaran las imagenes leidas
    while len(procesos_ejecucion) < procesos_paralelos and not ImagenesCola.empty():
        p = Process(name="Proceso {0}".format(indiceProceso),
                    target=ProcesadorImagen.procesar_imagen,
                    args=(indiceProceso, ImagenesCola, ImagenesGuardar_Cola, imagenesNoTexto, listaHash,)
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
