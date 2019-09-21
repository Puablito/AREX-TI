class Imagen:

    def __init__(self):
        self.__nombre = ""
        self.__extension = ""
        self.__path = ""
        self.__imagentipo = ""
        self.__hashes = {}
        self.__metadatos = dict()

    # Listar Atributos
    def imprimir(self):
        print("Nombre: {0}".format(self.get_nombre()))
        print("Extension: {0}".format(self.get_extension()))
        print("Path: {0}".format(self.get_path()))
        print("Tipo de Imagen: {0}".format(self.get_imagentipo()))
        print("Hashes: {0}".format(self.get_hashes()))
        print("Metadatos: {0}".format(self.get_metadatos()))

    # getters
    def get_nombre(self):
        return self.__nombre

    def get_extension(self):
        return self.__extension

    def get_path(self):
        return self.__path

    def get_imagentipo(self):
        return self.__imagentipo

    def get_hashes(self):
        return self.__hashes

    def get_metadatos(self):
        return self.__metadatos

    # setters
    def set_nombre(self, nombre):
        self.__nombre = nombre

    def set_extension(self, extension):
        self.__extension = extension

    def set_path(self, path):
        self.__path = path

    def set_imagentipo(self, imagentipo):
        self.__imagentipo = imagentipo

    def set_hashes(self, hashes):
        self.__hashes = hashes

    def set_metadatos(self, metadatos):
        self.__metadatos = metadatos
