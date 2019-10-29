import os
import imghdr
import datetime
import time
import argparse
import json
import ImagenAcciones
import Herramientas
import BaseDatos
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
    DirBase = args.dir
    '''

    # Realizo la conexión a la BD
    conexionBD = BaseDatos.Conexion()
    conexionOK = conexionBD.conectar("postgres", "arexti", "127.0.0.1", "5432", "arexti")
    #conexionOK = conexionBD.conectar("postgres", "1234", "127.0.0.1", "5432", "AREX-TI")
    if not conexionOK:
        print(conexionBD.error)

    # Recupero parametros necesarios para ejecurar el proceso
    """
    RtaBD[0] indica si la consulta se realizó OK o con "ERROR"
    RtaBD[1] si RtaBD[0] = "OK" contiene la respuesta de la consulta, caso contrario contiene el error obtenido
    """
    RtaBD = Herramientas.parametro_get(conexionBD, 'DIRECTORIOIMAGEN')
    if RtaBD[0] == "OK":
        DirBase = RtaBD[1][0]["valorTexto"]
    else:
        print(RtaBD[1])  ####################### VER QUE HACER EN ESTE CASO ######################

    RtaBD = Herramientas.parametro_get(conexionBD, 'LISTAEXTENSIONES')
    if RtaBD[0] == "OK":
        ListadoExtensiones = RtaBD[1][0]["valorTexto"]
    else:
        print(RtaBD[1])  ####################### VER QUE HACER EN ESTE CASO ######################

    RtaBD = Herramientas.parametro_get(conexionBD, 'TESSERACTPATH')
    if RtaBD[0] == "OK":
        tesseract_cmd = RtaBD[1][0]["valorTexto"]
    else:
        print(RtaBD[1])  ####################### VER QUE HACER EN ESTE CASO ######################

###################### Parametros hardcodeados ######################################
    #DirBase = 'C:/Users/Mariano-Dell/PycharmProjects/Imagenes/CapturasMarianOriginal/Nueva'
    listaHash = {"md5": "", "sha1": "", "sha256": ""}
    tipoProceso = "D"
    DirPrincipal = "PericiaPrueba\\Directorio1"
###################### FIN Parametros hardcodeados ######################################
    DirTemp = ""
    if tipoProceso == "A":
        RtaBD = Herramientas.parametro_get(conexionBD, 'DIRECTORIOIMAGENTEMP')
        if RtaBD[0] == "OK":
            DirTemp = RtaBD[1][0]["valorTexto"]
        else:
            print(RtaBD[1])  ####################### VER QUE HACER EN ESTE CASO ######################

    # Inicializo colas de trabajo multiproceso
    ImagenesCola = Queue()          # cola de imagenes a procesar
    ImagenesGuardar_Cola = Queue()  # cola de imagenes procesadas para guardar BD
    imagenesNoTexto = Queue()       # cola de imagenes no procesadas por no detectar texto en ellas

    # Lectura de las imagenes que van a ser procesadasa
    RtaCarga = ImagenAcciones.leer_imagenes(DirBase, DirTemp, ListadoExtensiones, ImagenesCola, tipoProceso, DirPrincipal)
    if RtaCarga[0] == "ERROR":
        print("DIO ERRROR, HAY QUE CORTAR LA EJECUCION Y GUARDAR LOG: {0}".format(RtaCarga[1]))

    """
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
    """
    ImagenesCola_cantidad = ImagenesCola.qsize()
    print(str(ImagenesCola_cantidad) + " Imagenes a procesar")
    TiempoInicial = datetime.datetime.now()

    # cantidad de procesos maximos a utilizar
    if os.cpu_count() < ImagenesCola_cantidad:
        procesos_paralelos = 4  ################################################# os.cpu_count()
    else:
        procesos_paralelos = ImagenesCola_cantidad

    procesos_ejecucion = []  # cantidad de procesos en ejecución
    indiceProceso = 1

    # Creación de los procesos que procesaran las imagenes leidas
    while len(procesos_ejecucion) < procesos_paralelos:
        p = Process(name="Proceso {0}".format(indiceProceso),
                    target=ImagenAcciones.procesar_imagen,
                    args=(indiceProceso, ImagenesCola, ImagenesGuardar_Cola, imagenesNoTexto, listaHash, tesseract_cmd,)
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
                    archivo_notexto.write(imagenesNoTexto.get() + "\n")

        # Guarda las Imagenes ya procesadas en la BD
        # Realizar mas pruebas (si la cola "ImagenesGuardar_Cola" se llena los procesos no terminan)

        while not ImagenesGuardar_Cola.empty():
            img_guardar = ImagenesGuardar_Cola.get()
# Guarda de a una imagen, ver de guardar por bloque de ser posible
            RtaBD = Herramientas.imagenInsertar(conexionBD, 1, img_guardar)
            if RtaBD[0] == "ERROR":
                print(RtaBD[1])
#
            print("Imagen: {0} - {1}".format(img_guardar.get_nombre(), img_guardar.get_imagentipo()))
#             print("////////////////////////////////////////////////////////////////////////")
#             print(img_guardar.get_path())
#             print("----------------------------------------")
#             for detalle in img_guardar.get_detalles():
#                 print("_____________________________________________________________________")
#                 print("Tipo globo: " + detalle.get_tipoGlobo())
#                 print(detalle.get_texto())
#                 print("_____________________________________________________________________")
#             print("////////////////////////////////////////////////////////////////////////")

        # Para no saturar el cpu, dormimos el ciclo durante 1 segundo
        time.sleep(1)

    print("WHILE: todos los procesos han terminado")

    TiempoFinal = datetime.datetime.now()
    print("Inicio: " + str(TiempoInicial))
    print("Fin:    " + str(TiempoFinal))
    print("Tiempo transcurrido: " + str(TiempoFinal - TiempoInicial))