import psycopg2
import json


class Conexion:
    __instanceBD = None

    def __init__(self):
        self.conectado = False
        self.error = ""

    def conectar(self):
        try:
            f = open("BDConect.txt", "r")
            contenido = f.read()
            f.close()
            DBdata = json.loads(contenido)

            host = DBdata['host']
            puerto = DBdata['puerto']
            bd = DBdata['BaseDeDatos']
            usuario = DBdata['usuario']
            clave = DBdata['clave']

        except FileNotFoundError:
            self.error = "Error al abrir la configuración de la BD"
            return False
        except:
            try:
                f.close()
                return False
            except:
                return False

        try:
            self.miconexion = psycopg2.connect(user=usuario,
                                               password=clave,
                                               host=host,
                                               port=puerto,
                                               database=bd)
            self.cursor = self.miconexion.cursor()
            self.conectado = True
            return True

        except psycopg2.Error:
            self.error = "Error al intentar conectarse a la Base de Datos "
        except Exception as e:
            self.error = "Error: {0}".format(e)
        return False

    def consulta(self, query, params=None, retorna=True):
        """
        Funcion que ejecuta una instruccion sql
        Tiene que recibir:
            - query
        Puede recibir:
            - params => tupla con las variables
            - retorna => devuelve los registros
        Devuelve False en caso de error, sino devuelve una lista de diccionarios,
            - la lista contiene los registros y dentro de cada elemento de la lista, hay un diccionario
             que contiene los campos del registro

        """
        if self.conectado:
            self.error = ""
            try:
                self.cursor.execute(query, params)
                # self.miconexion.commit()
                if retorna:
                    # convierte el resultado en un diccionario
                    result = []
                    columns = tuple([d[0] for d in self.cursor.description])
                    for row in self.cursor:
                        result.append(dict(zip(columns, row)))
                    return result
                return True
            except (Exception, psycopg2.Error) as e:
                self.error = "Error: {0} - {1}".format(e.pgerror, e.diag.message_detail)
        return False

    def conexionCommitRoll(self):
        try:
            self.miconexion.commit()
            return True
        except(Exception, psycopg2.Error) as e:
            self.miconexion.rollback()
            self.error = "Error: {0} - {1}".format(e.pgerror, e.diag.message_detail)
            return False

    def lastId(self):
        """
        Funcion que devuelve el ultimo id añadido
        """
        return self.cursor.fetchone()[0]

    def desconectar(self):
        self.conectado = False
        try:
            self.cursor.close()
        except:
            pass
        try:
            self.miconexion.close()
        except:
            pass
