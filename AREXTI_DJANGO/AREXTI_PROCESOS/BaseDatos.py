import psycopg2


class Conexion:

    def __init__(self, usuario, clave, host, puerto, bd):
        self.user = usuario
        self.password = clave
        self.host = host
        self.puerto = puerto
        self.database = bd

    def conectar(self):
        self.miconexion = psycopg2.connect(user=self.user,
                                            password=self.password,
                                            host=self.host,
                                            port=self.puerto,
                                            database=self.database)
        self.cursor = self.miconexion.cursor()

    def insertarImagen(self, imagen):
        query = ("""insert into "AREXTI_APP_imagen" (nombre, miniatura, referencia, extension, activo, pericia_id, "tipoImagen_id")"""
                 "values (%s, %s, %s, %s, %s, %s, %s)")
        # id = self.selectId()
        miniatura = ""
        nombre = imagen.get_nombre()
        extension = imagen.get_extension()
        referencia = imagen.get_path()
        tipoImagen = imagen.get_imagentipo()
        periciaId = 1
        imagen.get_hashes()
        imagen.get_metadatos()
        detalles = imagen.get_detalles()
        if tipoImagen == "C":
            tipoImagen = 1
        elif tipoImagen == "O":
            tipoImagen = 3
        else:
            tipoImagen = 2

        data = (nombre, miniatura, referencia, extension, 1, periciaId, tipoImagen)
        self.cursor.execute(query, data)
        self.miconexion.commit()

    def desconectar(self):
        self.miconexion.close()

    def selectId(self):
        query = (""" SELECT MAX(id) from "AREXTI_APP_imagen" """)
        self.cursor.execute(query)
        self.miconexion.commit()
        registro = self.cursor.fetchone()
        id = registro[0]+1
        return id