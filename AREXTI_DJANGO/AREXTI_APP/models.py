from django.db import models

# Create your models here.


class Proyecto(models.Model):
    IPP = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=500)
    fiscalia = models.CharField(max_length=100)
    responsable = models.CharField(max_length=60)
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
    descripcion = models.CharField(max_length=500)
    nombrePerito = models.CharField(max_length=60)
    fecha = models.DateField()
    tipoPericia = models.CharField(max_length=30, choices=tiposPericia, default='Movil')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, limit_choices_to={'activo': 1})
    activo = models.IntegerField(default=1)

    def __str__(self):
        return self.descripcion


class TipoImagen(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    activo = models.IntegerField(default=1)

    def __str__(self):
        return self.descripcion


class TipoHash(models.Model):
    nombre = models.CharField(max_length=20)
    activo = models.IntegerField(default=1)
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre


class Imagen(models.Model):
    pericia = models.ForeignKey(Pericia, on_delete=models.CASCADE)
    tipoImagen = models.ForeignKey(TipoImagen, on_delete=models.CASCADE, limit_choices_to={'activo': 1})
    hash = models.ManyToManyField(TipoHash, help_text="Seleccione un hash", through='ImagenHash', limit_choices_to={'activo': 1})
    nombre = models.CharField(max_length=256)
    miniatura = models.ImageField()
    thumbnail = models.BinaryField(blank=True, null=True)
    path = models.CharField(max_length=500)
    extension = models.CharField(max_length=5)
    clasificada = models.BooleanField(default=False)
    activo = models.IntegerField(default=1)

    def __str__(self):
        return self.nombre


class ImagenHash(models.Model):
    imagen = models.ForeignKey(Imagen, on_delete=models.CASCADE)
    tipoHash = models.ForeignKey(TipoHash, on_delete=models.CASCADE)
    valor = models.CharField(max_length=1000)


class TipoDetalle(models.Model):
    nombre = models.CharField(max_length=60)
    descripcion = models.CharField(max_length=10)


class ImagenDetalle(models.Model):
    imagen = models.ForeignKey(Imagen, on_delete=models.CASCADE)
    tipoDetalle = models.ForeignKey(TipoDetalle, on_delete=models.CASCADE)
    texto = models.CharField(max_length=200)




