import RedesNeuronales
import Hashes
import Metadatos
import ImagenProcesar
import Segmentacion
import logging
import sys
import os
import Herramientas

# Funcion que procesa la imagen recibida por paramentro
def procesar_imagen(procesoid, imagenes_cola, imagenes_guardar, imagenes_notexto, listado_hashes, tesseract_cmd):
    # instancio las RN
    try:
        rn_txt = RedesNeuronales.RedNeuronalTexto()
    except:
        logging.error('Error al instanciar la RN de Texto - ' + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

    try:
        rn_chat = RedesNeuronales.RedNeuronalChat()
    except:
        logging.error('Error al instanciar la RN de Chat - ' + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

    try:
        rn_mail = RedesNeuronales.RedNeuronalEmail()
    except:
        logging.error('Error al instanciar la RN de Email - ' + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

    # instancio el segmentador
    try:
        segmentador = Segmentacion.Segmentador(tesseract_cmd)
    except:
        logging.error('Error al instanciar el segmentador - ' + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

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

        # Verifica si posee texto o no
        try:
            tiene_texto = rn_txt.imagen_tiene_texto(img_path, img_nombre)
        except:
            msgerror = 'Error en RN Texto, al intentar predecir la imagen: ' + imagen_with_path + " ("
            logging.error(msgerror + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]) + ")")
            continue

        if not tiene_texto:  # Si la imagen NO posee texto
            imagenes_notexto.put(img_path + img_nombre)
        else:  # Si la imagen posee texto

            # Calcula Hashes
            try:
                listado_hashes = Hashes.calcular_hashes(listado_hashes, imagen_with_path)
                imagen_procesada.set_hashes(listado_hashes)
            except ValueError:
                msgerror = 'Error en los tipos de hash, verifiquelos e intente nuevamente. ('
                logging.error(msgerror + str(sys.exc_info()[0]) + " - " + str(sys.exc_info()[1]) + ")")
                break
            except:
                msgerror = 'Error al calcular los hash de la imagen: ' + imagen_with_path + " ("
                logging.error(msgerror + str(sys.exc_info()[0]) + " - " + str(sys.exc_info()[1]) + ")")
                continue

            # Extrae metadatos
            try:
                listado_metadatos = Metadatos.metadata_extraer(imagen_with_path)
                imagen_procesada.set_metadatos(listado_metadatos)
            except:
                msgerror = 'Error al extraer los metadatos de la imagen: ' + imagen_with_path + " ("
                logging.error(msgerror + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]) + ")")

            # Crea la miniatura
            try:
                thumbnail = Herramientas.miniaturaCrea(imagen_with_path, img_extension)
                imagen_procesada.set_thumbnail(thumbnail)
            except:
                msgerror = 'Error al crear la miniatura: ' + imagen_with_path + " ("
                logging.error(msgerror + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]) + ")")

            # Verifica si es de chat o no
            try:
                img_path = img_path + os.sep
                es_chat = rn_chat.imagen_es_chat(img_path, img_nombre)
            except:
                msgerror = 'Error en RN Chat, al intentar predecir la imagen: ' + imagen_with_path + " ("
                logging.error(msgerror + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]) + ")")
                continue
            segmentador.set_imagen(imagen_procesada)
            if es_chat:
                imagen_procesada.set_imagentipo("C")
                imagen_procesada.set_detalles(segmentador.segmentarChat())
                # Segmenta la imagen y extraer texto DE CHAT
            else:
                # Verifica si es de mail o no con la RN
                try:
                    img_path = img_path + os.sep
                    es_mail = rn_mail.imagen_es_email(img_path, img_nombre)
                except:
                    msgerror = 'Error en RN Mail, al intentar predecir la imagen: ' + imagen_with_path + " ("
                    logging.error(msgerror + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]) + ")")
                    continue

                if es_mail:
                    imagen_procesada.set_imagentipo("M")  # Segmenta la imagen y extraer texto DE MAIL
                    imagen_procesada.set_detalles(segmentador.segmentarMail())
                else:
                    imagen_procesada.set_imagentipo("O")  # Segmenta la imagen y extraer texto DE OTROS
                    imagen_procesada.set_detalles(segmentador.segmentarOtro())


            # LA CLASE IMAGEN PROCESADA INICIA EL PROCESO DE SEGMENTACION SEGUN EL TIPO DE IMAGEN SETEADO ARRIBA
            # imagen_segmentada = segmentador.procesarImagen(imagen_procesada)

            # Guarda en Cola para guardar en BD
            imagenes_guardar.put(imagen_procesada)
