import os
import imghdr
import datetime
import time
import ProcesadorImagen
from multiprocessing import Process, Queue


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
#rootDir = r'C:\Users\Mariano-Dell\PycharmProjects\Imagenes\CapturasMarian'
rootDir = 'F:\PythonProyects\SegmentacionIMG\Imagenes'
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
                    target=ProcesadorImagen.procesar_imagen,
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
