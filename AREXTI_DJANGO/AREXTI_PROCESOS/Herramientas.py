
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


def imagenInsertar(conexion, imagen):
    query = ("""insert into "AREXTI_APP_imagen" 
                (nombre, miniatura, referencia, extension, activo, pericia_id, "tipoImagen_id")"""
                "values (%s, %s, %s, %s, %s, %s, %s)")
    #     # id = self.selectId()
    #     miniatura = ""
    #     nombre = imagen.get_nombre()
    #     extension = imagen.get_extension()
    #     referencia = imagen.get_path()
    #     tipoImagen = imagen.get_imagentipo()
    #     periciaId = 1
    #     imagen.get_hashes()
    #     imagen.get_metadatos()
    #     detalles = imagen.get_detalles()
    #     if tipoImagen == "C":
    #         tipoImagen = 1
    #     elif tipoImagen == "O":
    #         tipoImagen = 3
    #     else:
    #         tipoImagen = 2
    #
    data = (nombre, miniatura, referencia, extension, 1, periciaId, tipoImagen)
    resultado = conexion.consulta(query, data)
    if resultado:
        return ["OK", resultado]
    else:
        return ["ERROR", conexion.error]