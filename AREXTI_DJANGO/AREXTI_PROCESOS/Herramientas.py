import cv2
import psycopg2

def parametro_get(conexion, parametro_id):
    query = """ SELECT "valorTexto","valorNumero","valorBooleano" 
                FROM "AREXTI_APP_parametros"
                WHERE "id"=%s;"""
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
                ("nombre", "miniatura", "thumbnail", "path", "extension", "activo", "pericia_id", "tipoImagen_id")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"""

    miniatura = ""
    nombre = imagen.get_nombre()
    extension = imagen.get_extension()
    path = imagen.get_path()

    tipoImagen = imagen.get_imagentipo()

    thumbnail = imagen.get_thumbnail()
    thumbnail_binary = psycopg2.Binary(thumbnail)  # lo hago binario o serializo

    data = (nombre, miniatura, thumbnail_binary, path, extension, 1, periciaid, tipoImagen)

    conexion.consulta(query, data, False)

    imagenId = conexion.lastId()
    # insert de las otras tablas
    hashes = imagen.get_hashes()
    hashesInsertar(hashes, imagenId, conexion)

    metadatos = imagen.get_metadatos()
    metadatosInsertar(metadatos, imagenId, conexion)

    detalles = imagen.get_detalles()
    detallesInsertar(detalles, imagenId, conexion)

    resultado = conexion.conexionCommitRoll()
    if resultado:
        return ["OK", resultado]
    else:
        # GUARDAR EN LOG????
        return ["ERROR", conexion.error]


def hashesInsertar(hashes, imagenId, conexion):
    query = """ INSERT INTO "AREXTI_APP_imagenhash" 
                (valor, imagen_id, "tipoHash_id")
                VALUES (%s, %s, %s)"""
    if hashes:
        for hash in hashes:
            tipoHash = hash
            valorHash = hashes[hash]
            data = (valorHash, imagenId, tipoHash)
            conexion.consulta(query, data, False)


def metadatosInsertar(metadatos, imagenId, conexion):
    query = """ INSERT INTO "AREXTI_APP_imagenmetadatos" 
                ("idMetadato", valor, imagen_id)
                VALUES (%s, %s, %s)"""
    if metadatos:
        for metadato in metadatos:
            idMetadato = metadato
            valorMetadato = metadatos[metadato]
            data = (idMetadato, valorMetadato, imagenId)
            conexion.consulta(query, data, False)


def detallesInsertar(detalles, imagenId, conexion):
    query = """ INSERT INTO "AREXTI_APP_imagendetalle" 
                (texto, imagen_id, "tipoDetalle_id")
                VALUES (%s, %s, %s)"""
    if detalles:
        for detalle in detalles:
            texto = detalle.get_texto()
            tipoDetalle = detalle.get_tipoDetalle()
            data = (texto, imagenId, tipoDetalle)
            conexion.consulta(query, data, False)


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


def imagenTipoActualizar(conexion, imagenId, imagentipo, detalles):
    # actualiza el tipo de imagen en tabla IMAGEN
    query = """ UPDATE "AREXTI_APP_imagen" 
                SET "tipoImagen_id" = %s
                WHERE id = %s;"""

    data = (imagentipo, imagenId)
    conexion.consulta(query, data, False)

    # Guarda el nuevo detalle de la Imagen
    detallesInsertar(detalles, imagenId, conexion)

    resultado = conexion.conexionCommitRoll()
    if resultado:
        return ["OK", resultado]
    else:
        return ["ERROR", conexion.error]


def imagenDetalleEliminar(conexion, imagenId):
    # Elimina el detalle de la imagen
    query = """ DELETE FROM "AREXTI_APP_imagendetalle" 
                WHERE id = %s;"""
    data = (imagenId,)
    conexion.consulta(query, data, False)
    resultado = conexion.conexionCommitRoll()
    if resultado:
        return ["OK", resultado]
    else:
        return ["ERROR", conexion.error]