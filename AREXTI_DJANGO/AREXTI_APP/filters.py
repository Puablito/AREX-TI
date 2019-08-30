from AREXTI_APP.models import Proyecto
import django_filters

class ProyectoFilter(django_filters.FilterSet):
    class Meta:
        model = Proyecto
        fields = ['IPP', 'fiscalia', 'descripcion', ]