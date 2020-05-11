from .models import Proyecto, Pericia, Imagen, TipoImagen, ImagenHash, ImagenDetalle, TipoDetalle, Metadatos, ImagenMetadatos
import django_filters
from django.db.models import Count, Sum
from django.db import models
from django import forms
from django_filters import widgets, filters
from django.db import connection
from . import funcionesdb


class ProyectoFilter(django_filters.FilterSet):
    descripcion = django_filters.CharFilter(lookup_expr='icontains', label='Descripción')
    fiscalia = django_filters.CharFilter(lookup_expr='icontains', label='Fiscalía')
    IPP = django_filters.CharFilter(lookup_expr='icontains', label='IPP')

    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        super().__init__(data, *args, **kwargs)

    class Meta:
        model = Proyecto
        fields = [ ]


class FechaRangoFilter(filters.Filter):
    field_class = forms.CharField

    def filter(self, qs, value):
        if value:
            if value is not None:
                self.lookup_expr = 'range'
                fechaIni = value.split('-')[0]
                fechaFin = value.split('-')[1]

                fechaIni = fechaIni.split('/')
                fechaIni = fechaIni[2].strip() + '-' + fechaIni[1].strip() + '-' \
                               + fechaIni[0].strip()

                fechaFin = fechaFin.split('/')
                fechaFin = fechaFin[2].strip() + '-' + fechaFin[1].strip() + '-' \
                               + fechaFin[0].strip()

                value = (fechaIni, fechaFin)
        return super().filter(qs, value)


class PericiaFilter(django_filters.FilterSet):
    fecha = FechaRangoFilter(label='Fecha')
    descripcion = django_filters.CharFilter(lookup_expr='icontains', label='Descripción')
    tipoPericia = django_filters.ChoiceFilter(choices=Pericia.tiposPericia, label='Tipo Pericia')

    def __init__(self, data, *args, **kwargs):
        # super(PericiaFilter, self).__init__(*args, **kwargs)

        if data is not None:
            # get a mutable copy of the QueryDict
            data = data.copy()

            for name, f in self.base_filters.items():
                initial = f.extra.get('initial')

                # filter param is either missing or empty, use initial as default
                if not data.get(name) and initial:
                    data[name] = initial

        super().__init__(data, *args, **kwargs)
        self.filters['tipoPericia'].extra.update(
            {'empty_label': 'Todas'})
        # self.form.initial['descripcion'] = 'aaaa'
        self.filters['proyecto'].extra.update(
            {'empty_label': 'Todos'})
        self.filters['proyecto'].label = 'IPP'

    class Meta:
        model = Pericia
        fields = ['tipoPericia', 'descripcion', 'proyecto', 'fecha', ]



class ImagenFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains', label='Nombre')
    extension = django_filters.CharFilter(lookup_expr='icontains', label='Extensión')
    tipoImagen = django_filters.ModelChoiceFilter(queryset=TipoImagen.objects.filter(activo=1), label='Tipo Imagen')
    hash = django_filters.CharFilter(method='filter_hash')

    class Meta:
        model = Imagen
        fields = ['hash']

    def __init__(self, *args, **kwargs):
        super(ImagenFilter, self).__init__(*args, **kwargs)
        self.filters['tipoImagen'].extra.update(
            {'empty_label': 'Todas'})

    def filter_hash(self, queryset, name, value):
        if value:
            queryset = Imagen.objects.filter(imagenhash__valor__contains=value)
        return queryset


def filter_not_empty(queryset, name, value):
    lookup = '__'.join([name, 'isnull'])
    return queryset.filter(**{lookup: False})


class ReporteFilter(django_filters.FilterSet):
    tipoImagen = django_filters.ModelMultipleChoiceFilter(queryset=TipoImagen.objects.filter(activo=1), label='Tipo Imagen')
    texto = django_filters.CharFilter(method='filter_texto', label='Palabra',)
    tipoDetalle = django_filters.ModelMultipleChoiceFilter(queryset=TipoDetalle.objects, label='Tipo Detalle')
    metadato = django_filters.ModelChoiceFilter(queryset=Metadatos.objects.distinct('idMeta'), label='Tipo Metadato', )
    proyecto = django_filters.ModelChoiceFilter(queryset=Proyecto.objects.filter(activo=1), label='IPP', )
    pericia = django_filters.ModelChoiceFilter(queryset=Pericia.objects.none(), label='Pericia', )
    valormeta = django_filters.CharFilter(label='Valor Metadato')
    limite = django_filters.NumberFilter(label='Cantidad de palabras')

    class Meta:
        model = Imagen
        fields = ['texto', 'pericia']

    def __init__(self, *args, **kwargs):
        super(ReporteFilter, self).__init__(*args, **kwargs)
        self.filters['pericia'].extra.update(
            {'empty_label': 'Todas'})
        self.filters['metadato'].extra.update(
            {'empty_label': 'Todos'})
        self.filters['proyecto'].extra.update(
            {'empty_label': 'Todos'})
        self.filters['proyecto'].label = 'IPP'
        # self.filters['texto'].extra.update(
        #     {'required': True})
        if 'proyecto' in self.data:
            try:
                proyectoId = int(self.data.get('proyecto'))
                self.filters['pericia'].queryset = Pericia.objects.filter(proyecto=proyectoId, activo=1).order_by('descripcion')
            except (ValueError, TypeError):
                pass
        else:
            self.filters['pericia'].queryset = Pericia.objects.none()


    def filter_queryset(self, queryset):
        """
        Filter the queryset with the underlying form's `cleaned_data`. You must
        call `is_valid()` or `errors` before calling this method.

        This method should be overridden if additional filtering needs to be
        applied to the queryset before it is cached.
        """
        filtros = self.form.cleaned_data
        palabra = filtros['texto']
        detalles = filtros['tipoDetalle']
        limite = filtros['limite']
        detallesfinal = ''
        for detalle in detalles:
            detallesfinal += detalle.id + '.'

        tipos = filtros['tipoImagen']
        tiposfinal = ''
        for tipo in tipos:
            tiposfinal += tipo.id + '.'

        pericia = filtros['pericia']
        if pericia is None:
            pericia = 0
        else:
            pericia = filtros['pericia'].id

        proyecto = filtros['proyecto']
        if proyecto is None:
            proyecto = 0
        else:
            proyecto = filtros['proyecto'].id

        metadato = filtros['metadato']
        if metadato is None:
            metadato = ''
        else:
            metadato = filtros['metadato'].idMeta
        valormetadato = filtros['valormeta']
        results = []
        if not(palabra is None or palabra == ''):
            try:
                results = funcionesdb.consulta('ocurrencias', [palabra, pericia, proyecto, tiposfinal, detallesfinal
                                                , metadato, valormetadato])

            except Exception as e:
                aa = e

        queryset = results
        return queryset
