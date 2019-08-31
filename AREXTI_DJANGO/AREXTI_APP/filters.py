from AREXTI_APP.models import Proyecto, Pericia
import django_filters


class ProyectoFilter(django_filters.FilterSet):

    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        # data.setdefault('IPP', '111')
        # data.setdefault('fiscalia', 'Fiscalia 1')
        # data.setdefault('order', '-added')
        super().__init__(data, *args, **kwargs)

    class Meta:
        model = Proyecto
        fields = ['IPP', 'fiscalia', 'descripcion', ]


class PericiaFilter(django_filters.FilterSet):
    fechas = django_filters.DateFromToRangeFilter(field_name='')

    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        # data.setdefault('IPP', '111')
        # data.setdefault('fiscalia', 'Fiscalia 1')
        # data.setdefault('order', '-added')
        super().__init__(data, *args, **kwargs)

    class Meta:
        model = Pericia
        fields = ['tipoPericia', 'descripcion', 'proyecto', 'fecha', ]