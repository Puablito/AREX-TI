from .models import Proyecto, Pericia, Imagen, TipoImagen, ImagenHash, ImagenDetalle, TipoDetalle
import django_filters
from django.db.models import Count, Sum
from django import forms
from django_filters import widgets, filters


class ProyectoFilter(django_filters.FilterSet):
    descripcion = django_filters.CharFilter(lookup_expr='icontains', label='Descripción')
    fiscalia = django_filters.CharFilter(lookup_expr='icontains', label='Fiscalía')
    IPP = django_filters.CharFilter(lookup_expr='icontains', label='IPP')

    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        # data.setdefault('IPP', '111')
        # data.setdefault('fiscalia', 'Fiscalia 1')
        # data.setdefault('order', '-added')
        super().__init__(data, *args, **kwargs)

    class Meta:
        model = Proyecto
        fields = [ ]


# class DateInput(forms.DateInput):
#     input_type = 'date'
#
#
# class FechaRangoWidget(widgets.SuffixedMultiWidget):
#     template_name = 'django_filters/widgets/multiwidget.html'
#     suffixes = ['ini', 'fin']
#
#     def __init__(self, attrs=None):
#         widgets = (DateInput, DateInput)
#         super().__init__(widgets, attrs)
#
#     def decompress(self, value):
#         if value:
#             return [value.start, value.stop]
#         return [None, None]
#
#
# class FechaRangoField(forms.MultiValueField):
#     widget = FechaRangoWidget
#
#     def __init__(self, fields=None, *args, **kwargs):
#         if fields is None:
#             fields = (
#                 forms.DateField(),
#                 forms.DateField())
#         super().__init__(fields, *args, **kwargs)
#
#     def compress(self, data_list):
#         if data_list:
#             return slice(*data_list)
#         return None


# class FechaRangoFilter(filters.RangeFilter):
#     field_class = FechaRangoField


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
    # fecha = django_filters.DateFromToRangeFilter()
    fecha = FechaRangoFilter(label='Fecha')
    descripcion = django_filters.CharFilter(lookup_expr='icontains', label='Descripción')
    tipoPericia = django_filters.ChoiceFilter(choices=Pericia.tiposPericia, label='Tipo Pericia')

    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        # data.setdefault('IPP', '111')
        # data.setdefault('fiscalia', 'Fiscalia 1')
        # data.setdefault('order', '-added')
        super().__init__(data, *args, **kwargs)

    class Meta:
        model = Pericia
        fields = ['tipoPericia', 'descripcion', 'proyecto', 'fecha', ]

    def __init__(self, *args, **kwargs):
        super(PericiaFilter, self).__init__(*args, **kwargs)
        self.filters['tipoPericia'].extra.update(
            {'empty_label': 'Todas'})
        self.filters['proyecto'].extra.update(
            {'empty_label': 'Todos'})


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
    # nombre = django_filters.CharFilter(lookup_expr='icontains', label='Nombre')
    # extension = django_filters.CharFilter(lookup_expr='icontains', label='Extensión')
    tipoImagen = django_filters.ModelChoiceFilter(queryset=TipoImagen.objects.filter(activo=1), label='Tipo Imagen')
    texto = django_filters.CharFilter(method='filter_texto', label='Palabra')
    tipoDetalle = django_filters.ModelChoiceFilter(method='filter_detalle',queryset=TipoDetalle.objects, label='Tipo Detalle')

    class Meta:
        model = Imagen
        fields = ['texto', 'pericia']

    def __init__(self, *args, **kwargs):
        super(ReporteFilter, self).__init__(*args, **kwargs)
        self.filters['tipoImagen'].extra.update(
            {'empty_label': 'Todas'})
        self.filters['pericia'].extra.update(
            {'empty_label': 'Todas'})
        self.filters['tipoDetalle'].extra.update(
            {'empty_label': 'Todos'})

    def filter_detalle(self, queryset, name, value):
        if value:
            queryset = Imagen.objects.filter(imagendetalle__id__icontains=value)
        return queryset

    def filter_texto(self, queryset, name, value):
        if value:
            # suma = Imagen.objects.filter(imagendetalle__texto__icontains=value).\
            #     annotate(num_ocurrencias=Count('id')).aggregate(suma_ocurrencias=Sum('num_ocurrencias'))['suma_ocurrencias']
            queryset = Imagen.objects.filter(imagendetalle__texto__icontains=value). \
                annotate(num_ocurrencias=Count('id')). \
                extra(
                select={
                    'suma_ocurrencias': """SELECT COUNT(*) FROM "AREXTI_APP_imagendetalle" WHERE texto ilike %s"""
                }, select_params=['%'+value+'%'])

        # , select_params=value   LIKE '%Pablito%'
        return queryset

    # def filter_queryset(self, queryset):
    #     queryset = queryset. \
    #             annotate(suma_ocurrencias=Sum('num_ocurrencias'))
    #     return queryset