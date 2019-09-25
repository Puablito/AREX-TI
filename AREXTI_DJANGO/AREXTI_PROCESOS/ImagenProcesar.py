import Segmentacion


class Imagen:

    def __init__(self):
        self.__nombre = ""
        self.__extension = ""
        self.__path = ""
        self.__imagentipo = ""
        self.__hashes = {}
        self.__metadatos = dict()
        self.__detalles = []
        # self.__segmentador = Segmentacion(self, 720)

    # Listar Atributos
    def imprimir(self):
        print("Nombre: {0}".format(self.get_nombre()))
        print("Extension: {0}".format(self.get_extension()))
        print("Path: {0}".format(self.get_path()))
        print("Tipo de Imagen: {0}".format(self.get_imagentipo()))
        print("Hashes: {0}".format(self.get_hashes()))
        print("Metadatos: {0}".format(self.get_metadatos()))

    # def procesarImagen(self):
    #     if self.__imagentipo == 'C':
    #         self.__detalles = self.__segmentador.segmentarChat()
    #     else:
    #         if self.tipoImagen == 'M':
    #             self.__detalles = self.__segmentador.segmentarMail()
    #         else:
    #             self.__detalles = self.__segmentador.segmentarOtro()

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

    def get_detalles(self):
        return self.__detalles

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

    def set_detalles(self, detalles):
        self.__detalles = detalles


class ImagenDetalle:

    def __init__(self):
        self.__imagen = 0
        self.__texto = ''
        self.__tipoGlobo = ''
        self.__nombre = ''
        self.__hora = None
        self.__mailFrom = ''
        self.__mailTo = ''

    # getters
    def get_imagen(self):
        return self.__imagen

    def get_texto(self):
        return self.__texto

    def get_tipoGlobo(self):
        return self.__tipoGlobo

    def get_nombre(self):
        return self.__nombre

    def get_hora(self):
        return self.__hora

    def get_mailFrom(self):
        return self.__mailFrom

    def get_mailTo(self):
        return self.__mailTo

    # setters
    def set_imagen(self, imagen):
        self.__imagen = imagen

    def set_texto(self, texto):
        self.__texto = texto

    def set_tipoGlobo(self, tipoGlobo):
        self.__tipoGlobo = tipoGlobo

    def set_nombre(self, nombre):
        self.__nombre = nombre

    def set_hora(self, hora):
        self.__hora = hora

    def set_mailFrom(self, mailFrom):
        self.__mailFrom = mailFrom

    def set_mailTo(self, mailTo):
        self.__mailTo = mailTo