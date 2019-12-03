import os
import shutil
import imghdr
import datetime
import sys
import logging
from . import RedesNeuronales, ImagenProcesar, Segmentacion, Herramientas, Hashes, Metadatos, BaseDatos
# import RedesNeuronales, ImagenProcesar, Segmentacion, Herramientas, Hashes, Metadatos, BaseDatos


def leer_imagenes(DirBaseDestino, DirTemp, ListadoExtensiones, ImagenesCola, tipoProceso, DirPrincipal, periciaid, conexionBD):
    """
    Recorre "DirPrincipal" con sus subdirectorios en busqueda de archivos de imagenes, el listado de tipo de imagenes
    soportados está guardado en una varialbe "ListadoExtensiones".
    Se analizan todos los archivos y los que son de tipo imagen se guardan en una cola "ImagenesCola"

    Formato de cada elemento de la cola "ImagenesCola"
       elemento 0 = Ruta absoluta del archivo, Ej: F:/Proyects/Imagenes
       elemento 1 = Nombre del archivo, Ej: Twitter.jpg
       elemento 2 = Extensión del archivo, Ej: jpeg

    DirBaseDestino = Dato parametrizado
    DirTemp = Directorio temporal donde se suben los archivos a procesar
    tipoProceso = A-> indica que es un upload de archivos, los cuales seran movidos dentro de la carpeta "DirPrincipal"
                  D-> indica que se carga un directorio completo en el servidor
    """
    resultadoOK = True
    msgError = ""
    if tipoProceso == "A":
        # Recupero el listado de las imagenes subidas desde la BD
        query = """ SELECT "file"
                    FROM "AREXTI_APP_uploadfile"
                    WHERE "periciaId"=%s;"""
        data = (periciaid,)
        UploadFileResultado = conexionBD.consulta(query, data)

        if UploadFileResultado:
            # Elimino la tabla de subida de archivos
            query = """ DELETE FROM "AREXTI_APP_uploadfile"
                        WHERE "periciaId"=%s;"""
            data = (periciaid,)
            ResultadoDelete = conexionBD.consulta(query, data)
            resultado = conexionBD.conexionCommitRoll()

            # Recorre la lista de imagenes subidas y las agrega al listado para cambiarla de directorio
            ImagenesDirTemp = []
            for r in UploadFileResultado:
                """
                    Se realiza un analisis para ver si la imagen se guardo en la carpeta raíz del temporal o 
                    en una subcarpeta de la misma.
                    1- Dentro del archivo leido de la tabla busco el ultimo separador de directorio
                       ( / o \\ ), si es que hay alguno.
                    2- Si no hay es porque es solo nombre de archivo. 
                       Si hay, se divide el nombre del archivo, en subpath y nombre 
                       Ej file/foto.jpg --> directorioTem = file -- archivoTemp = foto.jpg
                """
                x = r["file"].rfind(os.path.sep)
                if x == -1:
                    archivoTemp    = r["file"]
                    directorioTemp = ""
                else:
                    archivoTemp    = r["file"][x+1:]
                    directorioTemp = r["file"][:x]

                directorioTemp = DirTemp + os.path.sep + directorioTemp
                archivoAnalizar = directorioTemp + os.path.sep + archivoTemp

                try:
                    # Identifico si "archivoAnalizar" es imagen por el contenido y NO por la extensión
                    if imghdr.what(archivoAnalizar) is not None:
                        ext = imghdr.what(archivoAnalizar)
                        if ext.upper() in ListadoExtensiones:
                            # listado de todas las imagenes del directorio temporal
                            ImagenesDirTemp.append([directorioTemp, archivoTemp, ext])

                except Exception as e:
                    resultadoOK = False
                    msgError = "No se pudo analizar la imagen: {0} - {1}".format(archivoAnalizar, e)

            # si no dio error el analisis de las imagenes y
            # encontro alguna imagen, armo el directorio destino y lo creo
            if resultadoOK:
                if len(ImagenesDirTemp) > 0:
                    now = datetime.datetime.now()
                    dia = now.strftime("%Y")+now.strftime("%m")+now.strftime("%d")
                    hora= now.strftime("%H")+now.strftime("%M")+now.strftime("%S")
                    DirDestino = "Upload-"+dia+"-"+hora
                    pathDestino = DirBaseDestino + os.path.sep + DirPrincipal + os.path.sep + DirDestino

                    try:
                        if not os.path.exists(pathDestino):
                            os.makedirs(pathDestino)
                    except OSError as e:
                        resultadoOK = False
                        msgError = "No se pudo crear el directorio destino: {0} - {1}".format(pathDestino, e)

                    if resultadoOK:
                        # si existe el directorio de destino, muevo las imagenes del directorio temporal
                        # al mismo y se agrega a la cola de imagenes a procesar
                        try:
                            while len(ImagenesDirTemp) > 0:
                                imgTemp = ImagenesDirTemp.pop(0)
                                shutil.move(imgTemp[0] + os.path.sep + imgTemp[1], pathDestino + os.path.sep + imgTemp[1])
                                ImagenesCola.put([pathDestino, imgTemp[1], imgTemp[2]])
                        except Exception as e:
                            resultadoOK = False
                            msgError = "No se pudieron mover las imagenes al directorio destino: {0}".format(e)

                else:
                    resultadoOK = False
                    msgError = "La carpeta no posee imagenes para la pericia {0}".format(periciaid)

        else:
            resultadoOK = False
            msgError = "No se encontraron imagenes subidas para la pericia {0}".format(periciaid)

    elif tipoProceso == "D":
        pathDestino = DirBaseDestino + os.path.sep + DirPrincipal
        for dirName, subdirList, fileList in os.walk(pathDestino):
            for fname in fileList:
                archivo = dirName + os.path.sep + fname
                # Identifico si "archivo" es imagen por el contenido y NO por la extensión
                if imghdr.what(archivo) is not None:
                    ext = imghdr.what(archivo)
                    if ext.upper() in ListadoExtensiones:
                        ImagenesCola.put([dirName, fname, ext])

    if resultadoOK:
        return ["OK"]
    else:
        return ["ERROR", msgError]


# Funcion que procesa la imagen recibida por paramentro
def procesar_imagen(procesoid, imagenes_cola, imagenes_guardar, imagenes_notexto, listado_hashes, tesseract_cmd, RNTexto_procesa, mensajes_Cola):
    Is_OK = True
    # instancio las RN
    if RNTexto_procesa:
        try:
            rn_txt = RedesNeuronales.RedNeuronalTexto()
        except:
            Is_OK = False
            mensaje = ["ERROR", 'Error al instanciar la RN de Texto - {0} {1}'.format(sys.exc_info()[0],
                                                                                      sys.exc_info()[1])]
            mensajes_Cola.put(mensaje)
    try:
        rn_chat = RedesNeuronales.RedNeuronalChat()
    except:
        Is_OK = False
        mensaje = ["ERROR", 'Error al instanciar la RN de Chat - {0} {1}'.format(sys.exc_info()[0], sys.exc_info()[1])]
        mensajes_Cola.put(mensaje)

    try:
        rn_mail = RedesNeuronales.RedNeuronalEmail()
    except:
        Is_OK = False
        mensaje = ["ERROR", 'Error al instanciar la RN de Email - {0} {1}'.format(sys.exc_info()[0], sys.exc_info()[1])]
        mensajes_Cola.put(mensaje)

    # instancio el segmentador
    try:
        segmentador = Segmentacion.Segmentador(tesseract_cmd)
    except:
        Is_OK = False
        mensaje = ["ERROR", 'Error al instanciar el segmentador - {0} {1}'.format(sys.exc_info()[0], sys.exc_info()[1])]
        mensajes_Cola.put(mensaje)

    if Is_OK:
        while not imagenes_cola.empty():
            img_procesar = imagenes_cola.get()
            img_path = img_procesar[0] + os.sep
            img_nombre = img_procesar[1]
            img_extension = img_procesar[2]
            imagen_with_path = img_path + img_nombre

            imagen_procesada = ImagenProcesar.Imagen()
            imagen_procesada.set_nombre(img_procesar[1])
            imagen_procesada.set_extension(img_procesar[2])
            imagen_procesada.set_path(img_procesar[0])

            if RNTexto_procesa:
                # Verifica si posee texto o no
                try:
                    tiene_texto = rn_txt.imagen_tiene_texto(img_path, img_nombre)
                except:
                    mensaje = ["ERROR",
                               'Error en RN Texto, al predecir la imagen: {0} ({1} {2})'.format(imagen_with_path,
                                                                                                sys.exc_info()[0],
                                                                                                sys.exc_info()[1])]
                    mensajes_Cola.put(mensaje)
                    continue
            else:
                tiene_texto = ["OK", True]

            if tiene_texto[0] == "ERROR":
                mensaje = ["ERROR", 'Error en RN Texto ({0})'.format(tiene_texto[1])]
                mensajes_Cola.put(mensaje)
            else:
                # Si la imagen NO posee texto
                if not tiene_texto[1]:
                    imagenes_notexto.put(imagen_with_path)
                else:
                    # Si la imagen posee texto
                    # Calcula Hashes
                    try:
                        listado_hashes = Hashes.calcular_hashes(listado_hashes, imagen_with_path)
                        imagen_procesada.set_hashes(listado_hashes)
                    except ValueError:
                        mensaje = ["ERROR", 'Error en los tipos de hash. ({0} - {1})'.format(sys.exc_info()[0],
                                                                                             sys.exc_info()[1])]
                        mensajes_Cola.put(mensaje)
                        break

                    except:
                        mensaje = ["ERROR",
                                   'Error al calcular los hash de la imagen: {0} ({1} - {2})'.format(imagen_with_path,
                                                                                                     sys.exc_info()[0],
                                                                                                     sys.exc_info()[1])]
                        mensajes_Cola.put(mensaje)
                        continue

                    # Extrae metadatos
                    try:
                        listado_metadatos = Metadatos.metadata_extraer(imagen_with_path)
                        imagen_procesada.set_metadatos(listado_metadatos)
                    except:
                        mensaje = ["ERROR",
                                   'Error al extraer los metadatos de la imagen: {0} ({1} - {2})'.format(imagen_with_path,
                                                                                                         sys.exc_info()[0],
                                                                                                         sys.exc_info()[1])]
                        mensajes_Cola.put(mensaje)

                    # Crea la miniatura
                    try:
                        thumbnail = Herramientas.miniaturaCrea(imagen_with_path, img_extension)
                        imagen_procesada.set_thumbnail(thumbnail)
                    except:
                        mensaje = ["ERROR", 'Error al crear la miniatura: {0} ({1} - {2})'.format(
                            imagen_with_path, sys.exc_info()[0], sys.exc_info()[1])]
                        mensajes_Cola.put(mensaje)

                    # Inicializa el segmentador
                    segmentador.set_imagen(imagen_procesada)

                    # Verifica si es de chat o no
                    try:
                        img_path = img_path + os.sep
                        es_chat = rn_chat.imagen_es_chat(img_path, img_nombre)
                    except:
                        mensaje = ["ERROR",
                                   'Error en RN Chat, al predecir la imagen: {0} ({1} - {2})'.format(
                                       imagen_with_path, sys.exc_info()[0], sys.exc_info()[1])]
                        mensajes_Cola.put(mensaje)
                        continue

                    if es_chat[0] == "ERROR":
                        mensaje = ["ERROR", 'Error en RN Chat ({0})'.format(es_chat[1])]
                        mensajes_Cola.put(mensaje)
                        continue
                    else:
                        if es_chat[1]:
                            imagen_procesada.set_imagentipo("CHAT")
                            # Segmenta la imagen y extraer texto DE CHAT
                            RtaSeg = segmentador.segmentarChat()
                            if RtaSeg[0] == "ERROR":
                                mensaje = ["ERROR", 'Error ejecutando la segmentación de Chat - ({0})'.format(RtaSeg[1])]
                                mensajes_Cola.put(mensaje)
                                continue
                            else:
                                imagen_procesada.set_detalles(RtaSeg[1])
                        else:
                            # Verifica si es de mail
                            try:
                                img_path = img_path + os.sep
                                es_mail = rn_mail.imagen_es_email(img_path, img_nombre)
                            except:
                                mensaje = ["ERROR",
                                           'Error en RN Mail, al predecir la imagen: {0} ({1} - {2})'.format(
                                               imagen_with_path, sys.exc_info()[0], sys.exc_info()[1])]
                                mensajes_Cola.put(mensaje)
                                continue

                            if es_mail[0] == "ERROR":
                                mensaje = ["ERROR", 'Error en RN Mail ({0})'.format(es_mail[1])]
                                mensajes_Cola.put(mensaje)
                                continue
                            else:
                                if es_mail[1]:
                                    imagen_procesada.set_imagentipo("MAIL")
                                    # Segmenta la imagen y extraer texto DE MAIL
                                    RtaSeg = segmentador.segmentarMail()
                                    if RtaSeg[0] == "ERROR":
                                        mensaje = ["ERROR",
                                                   'Error ejecutando la segmentación de Mail - ({0})'.format(RtaSeg[1])]
                                        mensajes_Cola.put(mensaje)
                                        continue
                                    else:
                                        imagen_procesada.set_detalles(RtaSeg[1])

                                else:
                                    imagen_procesada.set_imagentipo("OTRO")
                                    # Segmenta la imagen y extraer texto DE OTROS
                                    RtaSeg = segmentador.segmentarOtro()
                                    if RtaSeg[0] == "ERROR":
                                        mensaje = ["ERROR",
                                                   'Error ejecutando la segmentación de Otros - ({0})'.format(RtaSeg[1])]
                                        mensajes_Cola.put(mensaje)
                                        continue
                                    else:
                                        imagen_procesada.set_detalles(RtaSeg[1])

                        mensaje = ["INFO", 'Fin del procesamiento de la imagen: {0}'.format(imagen_with_path)]
                        mensajes_Cola.put(mensaje)
                        # Guarda en Cola para guardar en BD
                        imagenes_guardar.put(imagen_procesada)


def cambiar_tipoimagen(imagenid,imagennombre, imagentipo):
    Is_OK = True

    # Crea la carpeta Logs
    DirAppBase = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'LOGS')
    try:
        if not os.path.exists(DirAppBase):
            os.makedirs(DirAppBase)
    except Exception:
        Is_OK = False

    if Is_OK:
        # Configuración del Log
        nombreArchivo = "CambioTipoImagen_{0}-{1}".format(imagenid, imagennombre)
        logging.basicConfig(handlers=[logging.FileHandler('{0}/{1}.txt'.format(DirAppBase, nombreArchivo), 'a', 'utf-8')],
                            format='%(asctime)s; %(levelname)s; %(message)s',
                            level=logging.INFO,
                            datefmt='%d-%b-%y %H:%M:%S')

        logging.info("----- Inicio del proceso cambio de tipo de imagen -----")
        logging.info("---- Parametros del proceso ----")
        logging.info("-- Imagen: {0}-{1}".format(imagenid, imagennombre))
        logging.info("-- Nuevo tipo de imagen : {0}".format(imagentipo))

        # Realizo la conexión a la BD
        conexionBD = BaseDatos.Conexion()
        Is_OK = conexionBD.conectar()
        if not Is_OK:
            logging.error(conexionBD.error)
        else:
            # Si se pudo conectar a la base de datos
            RtaBD = Herramientas.parametro_get(conexionBD, 'TESSERACTPATH')
            if RtaBD[0] == "OK":
                tesseract_cmd = RtaBD[1][0]["valorTexto"]
                logging.info("-- Ruta Tesseract: {0}".format(tesseract_cmd))
            else:
                Is_OK = False
                logging.error("Error en parametro: TESSERACTPATH (" + RtaBD[1] + ")")

    if Is_OK:
        # recupero la imagen a procesar
        imagen_procesar = ImagenProcesar.Imagen()
        query = """ SELECT "nombre","extension","path" 
                    FROM "AREXTI_APP_imagen"
                    WHERE "id"=%s;"""
        data = (imagenid,)
        resultado = conexionBD.consulta(query, data)
        logging.info("recupero la imagen a procesar")

        if resultado:
            # Creo el objeto Imagen para usarlo en el segmentador
            nombreImagen = resultado[0]["nombre"]
            imagen_procesar.set_nombre(nombreImagen)
            imagen_procesar.set_extension(resultado[0]["extension"])
            imagen_procesar.set_path(resultado[0]["path"])

            # instancio el segmentador
            try:
                segmentador = Segmentacion.Segmentador(tesseract_cmd)
            except:
                Is_OK = False
                logging.error('Error al instanciar el segmentador - ({0} - {1})'.format(sys.exc_info()[0],
                                                                                        sys.exc_info()[1]))

            if Is_OK:
                try:
                    # ejecuto el tipo de segmentación pasado por parametro
                    segmentador.set_imagen(imagen_procesar)

                    logging.info("Ejecuto el segmentador")

                    if imagentipo == "CHAT":
                        RtaSeg = segmentador.segmentarChat()
                        if RtaSeg[0] == "OK":
                            imagen_procesar.set_detalles(RtaSeg[1])
                        else:
                            logging.error('Error ejecutando la segmentación - ({0})'.format(RtaSeg[1]))
                            Is_OK = False

                    elif imagentipo == "MAIL":
                        RtaSeg = segmentador.segmentarMail()
                        if RtaSeg[0] == "OK":
                            imagen_procesar.set_detalles(RtaSeg[1])
                        else:
                            logging.error('Error ejecutando la segmentación - ({0})'.format(RtaSeg[1]))
                            Is_OK = False

                    elif imagentipo == "OTRO":
                        RtaSeg = segmentador.segmentarOtro()
                        if RtaSeg[0] == "OK":
                            imagen_procesar.set_detalles(RtaSeg[1])
                        else:
                            logging.error('Error ejecutando la segmentación - ({0})'.format(RtaSeg[1]))
                            Is_OK = False
                except:
                    Is_OK = False
                    logging.error('Error ejecutando la segmentación - ({0} - {1})'.format(sys.exc_info()[0],
                                                                                          sys.exc_info()[1]))

            if Is_OK:
                # Elimino el detalle actual
                Herramientas.imagenDetalleEliminar(conexionBD, imagenid)

                # Recupero y guardo el detalle nuevo, y actualizo el tipo de imagen
                detalles = imagen_procesar.get_detalles()
                Herramientas.imagenTipoActualizar(conexionBD, imagenid, imagentipo, detalles)
                resultado = conexionBD.conexionCommitRoll()

                if resultado:
                    logging.info("Cambio de tipo de la imagen {0}-{1} realizado correctamente".format(imagenid,
                                                                                                      nombreImagen))
                else:
                    logging.error("Error al cambiar el detalle de la imagen {0}-{1} ({2})".format(imagenid,
                                                                                                  nombreImagen,
                                                                                                  conexionBD.error))
    logging.info("----- Fin del proceso cambio de tipo de imagen -----")


# cambiar_tipoimagen(374,'mail 2.png',"OTRO")