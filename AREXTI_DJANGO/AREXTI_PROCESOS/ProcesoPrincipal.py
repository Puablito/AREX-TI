import os
import imghdr
import datetime
import time
import argparse
import json
import ImagenAcciones
import Herramientas
import BaseDatos
import logging
from multiprocessing import Process, Queue

# llamada de ejemplo (DESACTIVADAS)
# Notebook Pablo
# python parametros.py -j {\"hashes\":[{\"name\":\"sha1\"},{\"name\":\"sha256\"}],\"pericia\":1,\"urlFile\":\"Desktop/Capturas\",\"tabFrom\":\"A\"}

# Notebook Marian
# ProcesoPrincipal.py -t d -p 1 -a {\"md5\":\"\",\"sha1\":\"\",\"sha256\":\"\"} -d r'C:\Users\Mariano-Dell\PycharmProjects\Imagenes\CapturasMarian

if __name__ == '__main__':
    # Crea la carpeta Logs
    try:
        os.makedirs("./Logs")
    except FileExistsError:
        pass

    # Configuración del Log
    logging.basicConfig(filename='Logs/ProcesoPrincipal.csv',
                        filemode='a',
                        format='%(asctime)s; %(levelname)s; %(message)s',
                        level=logging.DEBUG,
                        datefmt='%d-%b-%y %H:%M:%S')

    '''
    # Se leen los parametros
    parser = argparse.ArgumentParser(description='Proceso principal')
    parser.add_argument('-j', '--json', required=True, type=str,
                        help='Listado de parametros en formato JSON')
    
    args = parser.parse_args()
    Parametros = json.loads(args.json)
    
    pericia = Parametros['pericia']
    procesotipo = Parametros['tabFrom']
    DirBase = Parametros['urlFile']
    
    # armar json con los hashes
    listaHash = dict()
    for item in Parametros['hashes']:
    listaHash.update({item['name']: ""})
    '''

    logging.info("----- Inicio del proceso priincipal -----")

    # Realizo la conexión a la BD
    conexionBD = BaseDatos.Conexion()
    Is_OK = conexionBD.conectar()
    if not Is_OK:
        logging.error(conexionBD.error)
        print(conexionBD.error)
    else:
        # Si se pudo conectar a la base de datos
        # Recupero parametros necesarios para ejecurar el proceso
        """
        RtaBD[0] indica si la consulta se realizó OK o con "ERROR"
        RtaBD[1] si RtaBD[0] = "OK" contiene la respuesta de la consulta, caso contrario contiene el error obtenido
        """
        RtaBD = Herramientas.parametro_get(conexionBD, 'DIRECTORIOIMAGEN')
        if RtaBD[0] == "OK":
            DirBase = RtaBD[1][0]["valorTexto"]
        else:
            Is_OK = False
            logging.error("Error en parametro: DIRECTORIOIMAGEN ("+RtaBD[1]+")")
            print("Error en parametro: DIRECTORIOIMAGEN ("+RtaBD[1]+")")

        RtaBD = Herramientas.parametro_get(conexionBD, 'LISTAEXTENSIONES')
        if RtaBD[0] == "OK":
            ListadoExtensiones = RtaBD[1][0]["valorTexto"]
        else:
            Is_OK = False
            logging.error("Error en parametro: LISTAEXTENSIONES (" + RtaBD[1] + ")")
            print("Error en parametro: LISTAEXTENSIONES ("+RtaBD[1]+")")

        RtaBD = Herramientas.parametro_get(conexionBD, 'TESSERACTPATH')
        if RtaBD[0] == "OK":
            tesseract_cmd = RtaBD[1][0]["valorTexto"]
        else:
            Is_OK = False
            logging.error("Error en parametro: TESSERACTPATH (" + RtaBD[1] + ")")
            print("Error en parametro: TESSERACTPATH ("+RtaBD[1]+")")

        RtaBD = Herramientas.parametro_get(conexionBD, 'PROCESOSPARALELOS')
        if RtaBD[0] == "OK":
            procesos_paralelos = RtaBD[1][0]["valorNumero"]
        else:
            Is_OK = False
            logging.error("Error en parametro: PROCESOSPARALELOS (" + RtaBD[1] + ")")
            print("Error en parametro: PROCESOSPARALELOS (" + RtaBD[1] + ")")

    ###################### Parametros hardcodeados ######################################
        listaHash = {"md5": "", "sha1": "", "sha256": ""}
        tipoProceso = "D"

        #Mariano
        DirPrincipal = "Todas"

        #Pablo
        # DirPrincipal = "PericiaPrueba"
    ###################### FIN Parametros hardcodeados ######################################
        DirTemp = ""
        if tipoProceso == "A":
            RtaBD = Herramientas.parametro_get(conexionBD, 'DIRECTORIOIMAGENTEMP')
            if RtaBD[0] == "OK":
                DirTemp = RtaBD[1][0]["valorTexto"]
            else:
                Is_OK = False
                logging.error("Error en parametro: DIRECTORIOIMAGENTEMP (" + RtaBD[1] + ")")
                print("Error en parametro: DIRECTORIOIMAGENTEMP ("+RtaBD[1]+")")  ####### VER QUE HACER EN ESTE CASO ##########

    # logging.info("-- Pericia: {0}".format(pericia))
    # logging.info("-- Tipo de proceso: {0}".format(procesotipo))
    # logging.info("-- Directorio a procesar: {0}".format(DirBase+ os.path.sep + DirPrincipal))

    if Is_OK:
        # Si no hay error en los parametros
        # Inicializo colas de trabajo multiproceso
        ImagenesCola = Queue()          # cola de imagenes a procesar
        ImagenesGuardar_Cola = Queue()  # cola de imagenes procesadas para guardar BD
        imagenesNoTexto_Cola = Queue()       # cola de imagenes no procesadas por no detectar texto en ellas

        # Lectura de las imagenes que van a ser procesadasa
        RtaCarga = ImagenAcciones.leer_imagenes(DirBase, DirTemp, ListadoExtensiones, ImagenesCola, tipoProceso, DirPrincipal)
        if RtaCarga[0] == "ERROR":
            Is_OK = False
            logging.error("Error leyendo las imagenes (" + RtaCarga[1] + ")")
            print("Error leyendo las imagenes: {0}".format(RtaCarga[1]))

    if Is_OK:
        """
        Inicio del procesamiento en paralelo
    
        1- Se crea un pool de procesos activos "procesos_ejecucion"
        2- Se crean los procesos, se inician y se agrega a "procesos_ejecucion"
        3- Mientras "procesos_ejecucion" tenga procesos activos:
            A- Para cada proceso revisamos si el proceso sigue vivo, en caso de que haya muerto lo recuperamos, 
                le quitamos los recursos y lo sacamos de "procesos_ejecucion"
            B- Verificamos si la cola "imagenesNoTexto_Cola" posee datos, de ser asi guardamos la información en el archivo LOG
            C- Verificamos si la cola "ImagenesGuardar_Cola" posee datos, de ser asi, se llama al proceso de guardado de imagen en BD 
         4- El proceso finaliza cuando "procesos_ejecucion" se encuentre vacio
        """
        ImagenesCola_cantidad = ImagenesCola.qsize()

        logging.info(str(ImagenesCola_cantidad) + " Imagenes a procesar")
        print(str(ImagenesCola_cantidad) + " Imagenes a procesar")
        TiempoInicial = datetime.datetime.now()

        # cantidad de procesos maximos a utilizar
        if procesos_paralelos > ImagenesCola_cantidad:
            procesos_paralelos = ImagenesCola_cantidad

        # Solo si se procesa un directorio la imagen es analizada por la RN de Texto
        if tipoProceso == "D":
            RNTexto_procesa = True
        else:
            RNTexto_procesa = False

        procesos_ejecucion = []  # cantidad de procesos en ejecución
        indiceProceso = 1

        # Creación de los procesos que procesaran las imagenes leidas
        while len(procesos_ejecucion) < procesos_paralelos:
            p = Process(name="Proceso {0}".format(indiceProceso),
                        target=ImagenAcciones.procesar_imagen,
                        args=(indiceProceso, ImagenesCola, ImagenesGuardar_Cola, imagenesNoTexto_Cola,
                              listaHash, tesseract_cmd, RNTexto_procesa,)
                        )
            p.start()
            procesos_ejecucion.append(p)
            logging.info("Se crea el proceso: {0}".format(indiceProceso))
            print("Agrega: " + p.name)
            indiceProceso += 1

        # Mientras haya procesos en ejecución
        while procesos_ejecucion:

            # Revisa si los procesos han muerto
            for proceso in procesos_ejecucion:
                if not proceso.is_alive():
                    logging.info("Se elimina el proceso: {0}".format(proceso.name))
                    print("Elimina: " + proceso.name)
                    # Recuperamos el proceso y lo sacamos de la lista
                    proceso.join()
                    procesos_ejecucion.remove(proceso)
                    del proceso

            # Guardado en archivo las imagenes que no se reconocieron con texto
            if not imagenesNoTexto_Cola.empty():
                with open("Logs/Log_imagenesSinTexto.txt", "a") as archivo_notexto:
                    while not imagenesNoTexto_Cola.empty():
                        archivo_notexto.write(imagenesNoTexto_Cola.get() + "\n")

            # Guarda las Imagenes ya procesadas en la BD
            # Realizar mas pruebas (si la cola "ImagenesGuardar_Cola" se llena los procesos no terminan)

            while not ImagenesGuardar_Cola.empty():
                img_guardar = ImagenesGuardar_Cola.get()
    # Guarda de a una imagen, ver de guardar por bloque de ser posible
                RtaBD = Herramientas.imagenInsertar(conexionBD, 1, img_guardar)
                if RtaBD[0] == "ERROR":
                    logging.error('Error al guardar la imagen, nombre: {0}'.format(img_guardar.get_nombre()))
                    print(RtaBD[1])

                print("Imagen: {0} - {1}".format(img_guardar.get_nombre(), img_guardar.get_imagentipo()))
            # Para no saturar el cpu, dormimos el ciclo durante 1 segundo
            time.sleep(1)
        conexionBD.desconectar()

        TiempoFinal = datetime.datetime.now()

        logging.info("-- Estadistica --")
        logging.info("Inicio del proceso: {0}".format(TiempoInicial))
        logging.info("Fin del proceso: {0}".format(TiempoFinal))
        logging.info("Tiempo transcurrido: {0}".format(TiempoFinal - TiempoInicial))
        logging.info("----- Fin del proceso priincipal pericia: -----")

        print("Todos los procesos han terminado")
        print("Inicio: " + str(TiempoInicial))
        print("Fin:    " + str(TiempoFinal))
        print("Tiempo transcurrido: " + str(TiempoFinal - TiempoInicial))