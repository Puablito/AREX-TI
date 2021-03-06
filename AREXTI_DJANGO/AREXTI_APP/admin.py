from django.contrib import admin

from .models import TipoImagen, TipoHash, TipoDetalle, Parametros, Metadatos, Diccionario, ImagenMetadatos


admin.site.site_header = 'Administrador AREX-TI'

admin.site.site_title = ''
# admin.site.index_title = 'AREXTI'



@admin.register(TipoHash)
class TipoImagenAdmin(admin.ModelAdmin):
    list_display = ('id', 'color')
    ordering = ('id',)
    search_fields = ('id',)


@admin.register(Parametros)
class TipoImagenAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion', 'valorTexto', 'valorNumero', 'valorBooleano')
    ordering = ('id',)
    search_fields = ('id', 'descripcion')


@admin.register(Metadatos)
class TipoImagenAdmin(admin.ModelAdmin):
    list_display = ('idMeta', 'idMetadatoImagen')
    ordering = ('id',)
    search_fields = ('id', 'idMetadatoImagen')


@admin.register(Diccionario)
class TipoImagenAdmin(admin.ModelAdmin):
    list_display = ('palabra',)
    ordering = ('palabra',)
    search_fields = ('id', 'palabra')