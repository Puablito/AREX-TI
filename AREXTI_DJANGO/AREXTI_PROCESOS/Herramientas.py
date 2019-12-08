import cv2
import os
from random import randint

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
                ("nombre", "miniatura", "path", "extension", "activo", "pericia_id", "tipoImagen_id")
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;"""

    nombre = imagen.get_nombre()
    extension = imagen.get_extension()
    path = imagen.get_path()

    tipoImagen = imagen.get_imagentipo()
    miniatura = imagen.get_miniatura()

    data = (nombre, miniatura, path, extension, 1, periciaid, tipoImagen)

    conexion.consulta(query, data, False)

    imagenId = conexion.lastId()
    # Si no pudo recuperar el ultimo ID Corta el guardado
    if imagenId == 0:
        return ["ERROR", conexion.error]

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


def miniaturaCrea(imagen, img_nombre, DirAppMiniatura):
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

    # Genero valor aleatorio y se lo agrego al nombre
    nroImg = randint(1, 99999999)
    nroImgS = "_{0}.".format(nroImg)
    img_nombre = img_nombre.replace(".", nroImgS)

    img_save = DirAppMiniatura + os.path.sep + img_nombre
    cv2.imwrite(img_save, img_resized)

    return img_save


def imagenTipoActualizar(conexion, imagenId, imagentipo, detalles):
    # actualiza el tipo de imagen en tabla IMAGEN
    query = """ UPDATE "AREXTI_APP_imagen" 
                SET "tipoImagen_id" = %s
                WHERE id = %s;"""

    data = (imagentipo, imagenId)
    conexion.consulta(query, data, False)

    # Guarda el nuevo detalle de la Imagen
    detallesInsertar(detalles, imagenId, conexion)


def imagenDetalleEliminar(conexion, imagenId):
    # Elimina el detalle de la imagen
    query = """ DELETE FROM "AREXTI_APP_imagendetalle" 
                WHERE imagen_id = %s;"""
    data = (imagenId,)
    conexion.consulta(query, data, False)
