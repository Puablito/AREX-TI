import cv2
import psycopg2

def parametro_get(conexion, parametro_id):
    query = """ SELECT "ParametroTexto","ParametroNumero","ParametroBoolean" 
                FROM "AREXTI_APP_parametros"
                WHERE "ParametroId"=%s;"""
    data = (parametro_id,)
    resultado = conexion.consulta(query, data)
    # return es una lista con 2 elementos [0]e[1], en cada elemento [1] es una lista de registros
    if resultado:
        return ["OK", resultado]
    else:
        return ["ERROR", conexion.error]


def imagenInsertar(conexion, periciaid,  imagen):
    # Inserta Tabla Imagen
    query = """ INSERT INTO "AREXTI_APP_imagen" 
                ("nombre", "thumbnail", "path", "extension", "activo", "pericia_id", "tipoImagen_id", "miniatura")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

    miniatura = ""
    nombre = imagen.get_nombre()
    extension = imagen.get_extension()
    path = imagen.get_path()

    tipoImagen = imagen.get_imagentipo()

    thumbnail = imagen.get_thumbnail()
    thumbnail_binary = psycopg2.Binary(thumbnail)  # lo hago binario o serializo

    data = (nombre, thumbnail_binary, path, extension, True, 1, periciaid, tipoImagen, miniatura)

    resultado = conexion.consulta(query, data, False)
    if resultado:
        return ["OK", resultado]
    else:
        return ["ERROR", conexion.error]
    # insert de las otras tablas
    hashes = imagen.get_hashes()
    metadatos = imagen.get_metadatos()
    detalles = imagen.get_detalles()

def hashesInsertar(hashes, imagenId):
    query = """ INSERT INTO "AREXTI_APP_imagen" 
                    (valor, imagen_id, "tipoHash_id")
                    VALUES (%s, %s, %s)"""
    id = imagenId
    for hash in hashes:
        1


def miniaturaCrea(imagen, ext):
    # leo la imagen
    img = cv2.imread(imagen, cv2.IMREAD_UNCHANGED)
    # calculo el porcentaje de escalado a partir del alto que quiero (64px)
    scale_percent = (64 * 100) / img.shape[0]
    # objtengo dimensiones
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    # genero la imagen reescalada
    img_resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    # Encodeo la imagen para guardarla en la BD
    retval, buf = cv2.imencode('.' + ext, img_resized)
    return buf

