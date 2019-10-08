
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
                ("nombre", "miniatura", "path", "extension", "clasificada", "activo", "pericia_id", "tipoImagen_id")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

    miniatura = ""
    nombre = imagen.get_nombre()
    extension = imagen.get_extension()
    path = imagen.get_path()

    tipoImagen = imagen.get_imagentipo()
    if tipoImagen == "C":
        tipoImagen = 1
    elif tipoImagen == "O":
        tipoImagen = 3
    else:
        tipoImagen = 2

    data = (nombre, miniatura, path, extension, True, 1, periciaid, tipoImagen)

    resultado = conexion.consulta(query, data, False)
    if resultado:
        return ["OK", resultado]
    else:
        return ["ERROR", conexion.error]
    # insert de las otras tablas
    # imagen.get_hashes()
    # imagen.get_metadatos()
    # detalles = imagen.get_detalles()
