import os
import imghdr
import datetime
import time
from multiprocessing import Process
import RedesNeuronales, Hashes, Metadatos

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
rootDir = 'F:\PythonProyects\SegmentacionIMG\Imagenes'

# Insertar tabla de procesos, analizar paquete logging

# Listado de extensiones que se van a procesar
ListadoExtensiones = ["JPG", "JPEG", "PNG", "GIF", "TIFF"]
ListaImagenes = []

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
                ListaImagenes.append([dirName, fname, ext])


''' 
Funcion que realiza todo el proceso
'''


def procesar_imagen(imagen_path, imagen_nombre):
    # Verifica si posee texto o no con la RN
    rn_txt = RedesNeuronales.RedNeuronalTexto()  # ver de usar singleton para no crear muchas instancias de la misma clase
    imagen_path = imagen_path + os.sep
    tiene_texto = rn_txt.imagen_tiene_texto(imagen_path, imagen_nombre)

    if not tiene_texto:  # Si la imagen NO posee texto
        pass  # guardar en log
    else:  # Si la imagen posee texto

        imagen_with_path = imagen_path + imagen_nombre

        # Calcula Hashes
        listado_hashes = {"md5": "", "sha1": "", "sha256": ""}
        listado_hashes = Hashes.calcular_hashes(listado_hashes, imagen_with_path)
        print("Imagen:" + str(imagen_nombre))
        print("Hashes: " + str(listado_hashes))

        # Extrae metadatos
        listado_metadatos = Metadatos.metadata_extraer(imagen_with_path)
        print("Imagen:" + str(imagen_nombre))
        print("Metadatos: " + str(listado_metadatos))

        # Verifica si es de chat o no con la RN
        rn_chat = RedesNeuronales.RedNeuronalChat()  # ver de usar singleton para no crear muchas instancias de la misma clase
        imagen_path = imagen_path + os.sep
        es_chat = rn_chat.imagen_es_chat(imagen_path, imagen_nombre)

        if es_chat:
            pass  # Segmenta la imagen y extraer texto DE CHAT
            print("ES CHAT :)")
        else:
            print("NO ES CHAT :(")
            '''
            # Verifica si es de mail o no con la RN
            rn_mail = RedesNeuronales.RedNeuronalEmail()  # ver de usar singleton para no crear muchas instancias de la misma clase
            imagen_path = imagen_path + os.sep
            es_mail = rn_mail.imagen_es_email(imagen_path, imagen_nombre)

            if es_mail:
                pass  # Segmenta la imagen y extraer texto DE MAIL
            else:
                pass  # Segmenta la imagen y extraer texto DE OTROS
            '''
        # Guarda en BD


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
    print(str(len(ListaImagenes))+" Imagenes a procesar")
    TiempoInicial = datetime.datetime.now()
    print("Inicio la RN")

    procesos_paralelos = os.cpu_count()  # cantidad de procesos maximos a utilizar
    procesos_ejecucion = []              # cantidad de procesos en ejecución
    imagen = ListaImagenes.pop(0)

    # se agrega el proceso a la lista de procesos activos
    p = Process(name="Proceso {0}".format(imagen[1]),
                target=procesar_imagen,
                args=(imagen[0], imagen[1],))
    p.start()
    procesos_ejecucion.append(p)

    # Mientras la piscina tenga procesos
    while procesos_ejecucion:
        for proceso in procesos_ejecucion:
            # Para cada proceso de la piscina revisamos si el proceso ha muerto
            if not proceso.is_alive():
                print("Elimina: "+proceso.name)
                # Recuperamos el proceso y lo sacamos de la piscina
                proceso.join()
                procesos_ejecucion.remove(proceso)
                del proceso

        while len(procesos_ejecucion) < procesos_paralelos and len(ListaImagenes) > 0:
            # Mientras la piscina no esté llena y el listado de imagenes no esté vacio, creo, inicio y 
            # agrego a la piscina yun nuevo proceso
            if len(ListaImagenes) > 0:
                imagen = ListaImagenes.pop(0)
                p = Process(name="Proceso {0}".format(imagen[1]),
                            target=procesar_imagen,
                            args=(imagen[0], imagen[1],))
                p.start()
                procesos_ejecucion.append(p)
                print("Agrega: " + p.name+" lista con " + str(len(ListaImagenes)) + " elementos")

        # Para no saturar, dormimos al padre durante 1 segundo
        time.sleep(1)

    print("WHILE: todos los procesos han terminado, cierro")
    TiempoFinal = datetime.datetime.now()
    print("Inicio: "+str(TiempoInicial))
    print("Fin:    "+str(TiempoFinal))
    print("Tiempo transcurrido: "+str(TiempoFinal - TiempoInicial))




