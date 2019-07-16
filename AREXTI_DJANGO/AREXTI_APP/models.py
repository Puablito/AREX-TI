from django.db import models

# Create your models here.
class Proyecto(models.Model):
    IPP = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    fiscalia = models.CharField(max_length=100)
    responsable = models.CharField(max_length=100)
    defensoria = models.CharField(max_length=100)
    juzgado = models.CharField(max_length=100)
    activo = models.BinaryField

    def __str__(self):
        return self.descripcion

class Pericia(models.Model):
    descripcion = models.CharField(max_length=200)
    nombrePerito = models.CharField(max_length=100)
    fecha = models.DateTimeField
    tipoPericia = models.CharField(max_length=100)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    activo = models.BinaryField

    def __str__(self):
        return self.descripcion

class TipoImagen(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    activo = models.BinaryField

    def __str__(self):
        return self.descripcion

class TipoHash(models.Model):
    nombre = models.CharField(max_length=100)
    funcion = models.CharField(max_length=200)
    activo = models.BinaryField

    def __str__(self):
        return self.nombre

class Imagen(models.Model):
    pericia = models.ForeignKey(Pericia, on_delete=models.CASCADE)
    tipoImagen = models.ForeignKey(TipoImagen, on_delete=models.CASCADE)
    hash = models.ManyToManyField(TipoHash, help_text="Seleccione un hash")
    nombre = models.CharField(max_length=100)
    miniatura = models.CharField(max_length=100)
    referencia = models.CharField(max_length=200)
    extension = models.CharField(max_length=10)
    clasificada = models.BinaryField
    activo = models.BinaryField

    def __str__(self):
        return self.nombre

class ImagenDetalle(models.Model):
    imagen = models.ForeignKey(Imagen, on_delete=models.CASCADE)
    texto = models.CharField(max_length=200)
    tipoGlobo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=100)
    hora = models.DateTimeField
    mailFrom = models.CharField(max_length=200)
    mailTo = models.CharField(max_length=200)
