import psycopg2


class Conexion:
    __instanceBD = None

    def __init__(self):
        self.conectado = False
        self.error = ""

    def conectar(self, usuario, clave, host, puerto, bd):
        try:
            self.miconexion = psycopg2.connect(user=usuario,
                                               password=clave,
                                               host=host,
                                               port=puerto,
                                               database=bd)
            self.cursor = self.miconexion.cursor()
            self.conectado = True
            return True

        except (Exception, psycopg2.Error) as e:
            self.error = "Error: %s" % e
        except:
            self.error = "Error desconocido"
        return False

    def consulta(self, query, params=None, execute=True):
        """
        Funcion que ejecuta una instruccion sql
        Tiene que recibir:
            - query
        Puede recibir:
            - params => tupla con las variables
            - execute => devuelve los registros
        Devuelve False en caso de error, sino devuelve una lista de diccionarios,
            - la lista contiene los registros y dentro de cada elemento de la lista, hay un diccionario
             que contiene los campos del registro

        """
        if self.conectado:
            self.error = ""
            try:
                self.cursor.execute(query, params)
                self.miconexion.commit()
                if execute:
                    # convierte el resultado en un diccionario
                    result = []
                    columns = tuple([d[0] for d in self.cursor.description])
                    for row in self.cursor:
                        result.append(dict(zip(columns, row)))
                    return result
                return True
            except (Exception, psycopg2.Error) as e:
                self.error = "Error: %s" % e
        return False

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
