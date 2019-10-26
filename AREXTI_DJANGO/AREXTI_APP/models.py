from django.db import models

# Create your models here.


class Proyecto(models.Model):
    IPP = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    fiscalia = models.CharField(max_length=100)
    responsable = models.CharField(max_length=100)
    defensoria = models.CharField(max_length=100)
    juzgado = models.CharField(max_length=100)
    activo = models.IntegerField(default=1)

    def __str__(self):
        return self.descripcion


class Pericia(models.Model):
    tiposPericia = (
        ('Movil', 'Movil'),
        ('Investigacion', 'Investigacion'),
        ('Otro', 'Otro'),
    )
    descripcion = models.CharField(max_length=200)
    nombrePerito = models.CharField(max_length=100)
    fecha = models.DateField()
    tipoPericia = models.CharField(max_length=30, choices=tiposPericia, default='Movil')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, limit_choices_to={'activo': 1})
    activo = models.IntegerField(default=1)

    def __str__(self):
        return self.descripcion


class TipoImagen(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    activo = models.IntegerField(default=1)

    def __str__(self):
        return self.nombre


class TipoHash(models.Model):
    nombre = models.CharField(max_length=100)
    funcion = models.CharField(max_length=200)
    activo = models.IntegerField(default=1)
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre


class Imagen(models.Model):
    pericia = models.ForeignKey(Pericia, on_delete=models.CASCADE)
    tipoImagen = models.ForeignKey(TipoImagen, on_delete=models.CASCADE, limit_choices_to={'activo': 1})
    hash = models.ManyToManyField(TipoHash, help_text="Seleccione un hash", through='ImagenHash')
    nombre = models.CharField(max_length=100)
    miniatura = models.CharField(max_length=100)
    referencia = models.CharField(max_length=200)
    extension = models.CharField(max_length=10)
    activo = models.IntegerField(default=1)

    def __str__(self):
        return self.nombre

    def get_datos(self, tipoHashId):
        return self.imagenhash_set.filter(tipoHash=tipoHashId)


class ImagenHash(models.Model):
    imagen = models.ForeignKey(Imagen, on_delete=models.CASCADE)
    tipoHash = models.ForeignKey(TipoHash, on_delete=models.CASCADE)
    valor = models.CharField(max_length=1000)


class ImagenDetalle(models.Model):
    imagen = models.ForeignKey(Imagen, on_delete=models.CASCADE)
    texto = models.CharField(max_length=200)
    tipoGlobo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=100)
    hora = models.DateTimeField
    mailFrom = models.CharField(max_length=200)
    mailTo = models.CharField(max_length=200)


class ImagenFile(object):
    periciaId = models.IntegerField()
    fileUrl = models.CharField(max_length=200)
    hashList = models.CharField(max_length=5000)

