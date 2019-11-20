from django.db import models
# Create your models here.


class Proyecto(models.Model):
    IPP = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=500)
    fiscalia = models.CharField(max_length=100, blank=True)
    responsable = models.CharField(max_length=60, blank=True)
    defensoria = models.CharField(max_length=100, blank=True)
    juzgado = models.CharField(max_length=100, blank=True)
    activo = models.IntegerField(default=1)

    class Meta:
        indexes = [models.Index(fields=['IPP']),
                   models.Index(fields=['descripcion']),
                   models.Index(fields=['fiscalia']),
                   models.Index(fields=['IPP', 'descripcion', 'fiscalia'])]

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
    directorio = models.CharField(max_length=100, blank=True)

    class Meta:
        indexes = [models.Index(fields=['proyecto']),
                   models.Index(fields=['descripcion']),
                   models.Index(fields=['fecha']),
                   models.Index(fields=['proyecto', 'descripcion', 'fecha'])]

    def __str__(self):
        return self.descripcion


class TipoImagen(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    descripcion = models.CharField(max_length=100, blank=True)
    activo = models.IntegerField(default=1)

    def __str__(self):
        return self.id


class TipoHash(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    activo = models.IntegerField(default=1)
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.id


class Imagen(models.Model):
    pericia = models.ForeignKey(Pericia, on_delete=models.CASCADE)
    tipoImagen = models.ForeignKey(TipoImagen, on_delete=models.CASCADE, limit_choices_to={'activo': 1})
    hash = models.ManyToManyField(TipoHash, help_text="Seleccione un hash", through='ImagenHash')
    nombre = models.CharField(max_length=256)
    miniatura = models.ImageField(blank=True)
    thumbnail = models.BinaryField(blank=True, null=True)
    path = models.CharField(max_length=500)
    extension = models.CharField(max_length=5)
    activo = models.IntegerField(default=1)

    class Meta:
        indexes = [models.Index(fields=['nombre']),
                   models.Index(fields=['extension']),
                   models.Index(fields=['tipoImagen']),
                   models.Index(fields=['nombre', 'extension', 'tipoImagen'])]

    def __str__(self):
        return self.nombre

    def get_datos(self, tipoHashId):
        return self.imagenhash_set.filter(tipoHash=tipoHashId)

    def get_detalle(self, imagen):
        return self.imagendetalle_set.filter(imagen=imagen)


class ImagenHash(models.Model):
    imagen = models.ForeignKey(Imagen, on_delete=models.CASCADE)
    tipoHash = models.ForeignKey(TipoHash, on_delete=models.CASCADE)
    valor = models.CharField(max_length=1000)


class TipoDetalle(models.Model):
    id = models.CharField(max_length=60, primary_key=True)
    descripcion = models.CharField(max_length=100)
    def __str__(self):
        return self.id


class ImagenDetalle(models.Model):
    imagen = models.ForeignKey(Imagen, on_delete=models.CASCADE)
    tipoDetalle = models.ForeignKey(TipoDetalle, on_delete=models.CASCADE)
    texto = models.TextField(max_length=100000)


class Log(models.Model):
    periciaId = models.IntegerField(blank=True)
    tipo = models.CharField(max_length=4, blank=True)
    descripcion = models.CharField(max_length=2048, blank=True)
    imagenPath = models.CharField(max_length=512, blank=True)
    imagenNombre = models.CharField(max_length=256, blank=True)


class Parametros(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    descripcion = models.CharField(max_length=128, blank=True)
    valorTexto = models.CharField(max_length=512, blank=True, null=True)
    valorNumero = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    valorBooleano = models.BooleanField(blank=True, null=True)


class Metadatos(models.Model):
    idMeta = models.CharField(max_length=50)
    idMetadatoImagen = models.CharField(max_length=50)

    class Meta:
        unique_together = (('idMeta', 'idMetadatoImagen'),)

    def __str__(self):
        return self.idMeta

class ImagenMetadatos(models.Model):
    imagen = models.ForeignKey(Imagen, on_delete=models.CASCADE)
    idMetadato = models.CharField(max_length=50)
    valor = models.CharField(max_length=512)

    class Meta:
        indexes = [models.Index(fields=['idMetadato']),
                   models.Index(fields=['valor']),
                   models.Index(fields=['idMetadato', 'valor'])]
    def __str__(self):
        return self.valor


class ImagenFile(object):
    periciaId = models.IntegerField()
    fileUrl = models.CharField(max_length=200)
    hashList = models.CharField(max_length=5000)

