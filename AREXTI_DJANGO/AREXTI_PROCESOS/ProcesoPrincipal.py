import os
import datetime
import time
import logging
from AREXTI_PROCESOS import ImagenAcciones, Herramientas, BaseDatos
# import ImagenAcciones, Herramientas, BaseDatos
from multiprocessing import Process, Queue


def proceso_Principal(periciaid, periciaNombre, tipoProceso, DirPrincipal, listaHash, periciaDir):
    if __name__ == 'AREXTI_PROCESOS.ProcesoPrincipal':
        Is_OK = True

        # Crea la carpeta Logs General
        DirAppBase = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'LOGS')
        try:
            if not os.path.exists(DirAppBase):
                os.makedirs(DirAppBase)
        except Exception:
            Is_OK = False

        if Is_OK:
            # Configuración del Log General
            fhGeneral = logging.FileHandler('{0}/Log_Errores.txt'.format(DirAppBase), 'a', 'utf-8')
            fhGeneral.setLevel(logging.WARNING)
            fhGeneral.setFormatter(logging.Formatter('%(asctime)s; %(levelname)s; %(message)s'))

            loggerGeneral = logging.getLogger('LogGeneral')
            loggerGeneral.setLevel(logging.INFO)
            loggerGeneral.addHandler(fhGeneral)

            # Realizo la conexión a la BD
            conexionBD = BaseDatos.Conexion()
            Is_OK = conexionBD.conectar()

            if not Is_OK:
                loggerGeneral.error(conexionBD.error)
            else:
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
                    loggerGeneral.error("Error en parametro: DIRECTORIOIMAGEN ("+RtaBD[1]+")")

                RtaBD = Herramientas.parametro_get(conexionBD, 'LISTAEXTENSIONES')
                if RtaBD[0] == "OK":
                    ListadoExtensiones = RtaBD[1][0]["valorTexto"]
                else:
                    Is_OK = False
                    loggerGeneral.error("Error en parametro: LISTAEXTENSIONES (" + RtaBD[1] + ")")

                RtaBD = Herramientas.parametro_get(conexionBD, 'TESSERACTPATH')
                if RtaBD[0] == "OK":
                    tesseract_cmd = RtaBD[1][0]["valorTexto"]
                else:
                    Is_OK = False
                    loggerGeneral.error("Error en parametro: TESSERACTPATH (" + RtaBD[1] + ")")

                RtaBD = Herramientas.parametro_get(conexionBD, 'PROCESOSPARALELOS')
                if RtaBD[0] == "OK":
                    procesos_paralelos = RtaBD[1][0]["valorNumero"]
                else:
                    Is_OK = False
                    loggerGeneral.error("Error en parametro: PROCESOSPARALELOS (" + RtaBD[1] + ")")

                DirTemp = ""
                if tipoProceso == "A":
                    RtaBD = Herramientas.parametro_get(conexionBD, 'DIRECTORIOIMAGENTEMP')
                    if RtaBD[0] == "OK":
                        DirTemp = RtaBD[1][0]["valorTexto"]
                    else:
                        Is_OK = False
                        loggerGeneral.error("Error en parametro: DIRECTORIOIMAGENTEMP (" + RtaBD[1] + ")")

        # Si no hay error en los parametros
        if Is_OK:
            # Configuración del Log de la Pericia
            DirAppPericia = DirBase + os.path.sep + periciaDir
            fhPericia = logging.FileHandler('{0}/ProcesoImagenes.txt'.format(DirAppPericia), 'a', 'utf-8')
            fhPericia.setLevel(logging.INFO)
            fhPericia.setFormatter(logging.Formatter('%(asctime)s; %(levelname)s; %(message)s'))

            loggerPericia = logging.getLogger('LogPericia')
            loggerPericia.setLevel(logging.INFO)
            loggerPericia.addHandler(fhPericia)

            # Creo diccionario de hashes
            dic = dict()
            for hashTipo in listaHash:
                dic.update({hashTipo: ""})
            listaHash = dic

            # Inicializo log de la pericia
            loggerPericia.info("**************************************************************************************")
            loggerPericia.info("----- Inicio Procesamiento Imagenes -----")
            loggerPericia.info("---- Parametros generales ----")
            loggerPericia.info("-- Directorio Base: {0}".format(DirBase))
            loggerPericia.info("-- Lista de Extensiones validas: {0}".format(ListadoExtensiones))
            loggerPericia.info("-- Ruta Tesseract: {0}".format(tesseract_cmd))
            loggerPericia.info("-- Cantidad Procesos paralelos: {0}".format(procesos_paralelos))
            if tipoProceso == "A":
                loggerPericia.info("-- Directorio Temporal: {0}".format(DirTemp))

            loggerPericia.info("---- Parametros del proceso ----")
            loggerPericia.info("-- Pericia: {0}-{1}".format(periciaid, periciaNombre))
            if tipoProceso == "A":
                loggerPericia.info("-- Tipo de proceso: Archivos")
            else:
                loggerPericia.info("-- Tipo de proceso: Directorio")
            loggerPericia.info("-- Hashes a aplicar: {0}".format(listaHash))

            TiempoInicial = datetime.datetime.now()

            # Inicializo colas de trabajo multiproceso
            ImagenesCola = Queue()          # cola de imagenes a procesar
            ImagenesGuardar_Cola = Queue()  # cola de imagenes procesadas para guardar BD
            imagenesNoTexto_Cola = Queue()  # cola de imagenes no procesadas por no detectar texto en ellas

            # Lectura de las imagenes que van a ser procesadasa
            RtaCarga = ImagenAcciones.leer_imagenes(DirBase, DirTemp, ListadoExtensiones, ImagenesCola, tipoProceso, DirPrincipal, periciaid, conexionBD)
            if RtaCarga[0] == "ERROR":
                Is_OK = False
                loggerPericia.error("Error al leer las imagenes (" + RtaCarga[1] + ")")

        if Is_OK:
            """
            Inicio del procesamiento en paralelo
        
            1- Se crea un pool de procesos activos "procesos_ejecucion"
            2- Se crean los procesos, se inician y se agrega a "procesos_ejecucion"
            3- Mientras "procesos_ejecucion" tenga procesos activos:
                A- Para cada proceso revisamos si el proceso sigue vivo, en caso de que haya muerto lo recuperamos, 
                    le quitamos los recursos y lo sacamos de "procesos_ejecucion"
                B- Verificamos si la cola "imagenesNoTexto_Cola" posee datos, de ser asi guardamos la información en 
                   el archivo LOG
                C- Verificamos si la cola "ImagenesGuardar_Cola" posee datos, de ser asi, se llama al proceso de 
                   guardado de imagen en BD 
             4- El proceso finaliza cuando "procesos_ejecucion" se encuentre vacio
            """
            ImagenesCola_cantidad = ImagenesCola.qsize()

            loggerPericia.info("{0} Imagenes a procesar".format(ImagenesCola_cantidad))

            # Cantidad de procesos maximos a utilizar
            if procesos_paralelos > ImagenesCola_cantidad:
                procesos_paralelos = ImagenesCola_cantidad

            # Solo si se procesa un directorio la imagen es analizada por la RN de Texto
            if tipoProceso == "D":
                RNTexto_procesa = True
            else:
                RNTexto_procesa = False

            mensajes_Cola = Queue()
            procesos_ejecucion = []  # cantidad de procesos en ejecución
            indiceProceso = 1

            # Creación de los procesos que procesaran las imagenes leidas
            while len(procesos_ejecucion) < procesos_paralelos:
                p = Process(name="Proceso {0}".format(indiceProceso),
                            target=ImagenAcciones.procesar_imagen,
                            args=(indiceProceso, ImagenesCola, ImagenesGuardar_Cola, imagenesNoTexto_Cola,
                                  listaHash, tesseract_cmd, RNTexto_procesa, mensajes_Cola,)
                            )
                p.start()
                procesos_ejecucion.append(p)
                loggerPericia.info("Se crea el proceso: {0}".format(indiceProceso))
                indiceProceso += 1

            # Mientras haya procesos en ejecución
            while procesos_ejecucion:

                # Guardado en archivo las imagenes que no se reconocieron con texto
                if not imagenesNoTexto_Cola.empty():
                    with open('{0}/ImagenesSinTexto.txt'.format(DirAppPericia), "a") as archivo_notexto:
                        while not imagenesNoTexto_Cola.empty():
                            fecha = time.strftime("%d-%m-%Y %H:%M:%S")
                            archivo_notexto.write("{0}; {1}; \n".format(fecha, imagenesNoTexto_Cola.get()))

                # Guarda los mensajes en log
                while not mensajes_Cola.empty():
                    mensaje = mensajes_Cola.get()
                    if mensaje[0] == "INFO":
                        loggerPericia.info(mensaje[1])
                    elif mensaje[0] == "ERROR":
                        loggerPericia.error(mensaje[1])

                # Guarda las Imagenes ya procesadas en la BD
                while not ImagenesGuardar_Cola.empty():
                    img_guardar = ImagenesGuardar_Cola.get()
                    # Guarda de a una imagen
                    RtaBD = Herramientas.imagenInsertar(conexionBD, periciaid, img_guardar)
                    if RtaBD[0] == "ERROR":
                        mjeError = RtaBD[1].replace("\n", ",")
                        loggerPericia.error('Error al guardar la imagen en la Base de Datos, nombre: {0} - ({1})'.format(
                            img_guardar.get_nombre(), mjeError))

                    print("Imagen: {0} - {1}".format(img_guardar.get_nombre(), img_guardar.get_imagentipo()))

                # Revisa si los procesos han muerto
                for proceso in procesos_ejecucion:
                    if not proceso.is_alive():
                        loggerPericia.info("Se elimina el proceso: {0}".format(proceso.name))
                        # Recuperamos el proceso y lo sacamos de la lista
                        proceso.join()
                        procesos_ejecucion.remove(proceso)
                        del proceso

                # Para no saturar el cpu, dormimos el ciclo durante 1 segundo
                time.sleep(1)
            conexionBD.desconectar()

            TiempoFinal = datetime.datetime.now()

            loggerPericia.info("-- Estadistica --")
            loggerPericia.info("Inicio del proceso: {0}".format(TiempoInicial))
            loggerPericia.info("Fin del proceso: {0}".format(TiempoFinal))
            loggerPericia.info("Tiempo transcurrido: {0}".format(TiempoFinal - TiempoInicial))
            loggerPericia.info("----- Fin del proceso principal pericia: {0}-{1} -----".format(periciaid, periciaNombre))
            loggerPericia.info("**************************************************************************************")
