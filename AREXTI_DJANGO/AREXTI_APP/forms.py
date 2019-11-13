from django import forms
from AREXTI_APP.models import Proyecto, Pericia, Imagen, TipoImagen


class DateInput(forms.DateInput):
    input_type = 'date'


class ProyectoForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Proyecto

        fields = [
            'IPP',
            'descripcion',
            'fiscalia',
            'responsable',
            'defensoria',
            'juzgado',
        ]

        labels = {
            'IPP': 'IPP',
            'descripcion': 'Descripcion',
            'fiscalia': 'Fiscalia',
            'responsable': 'Responsable',
            'defensoria': 'Defensoria',
            'juzgado': 'Juzgado',
        }

        widgets = {
            'IPP': forms.TextInput(attrs={'class': 'form-control', 'id': 'IPP'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'fiscalia': forms.TextInput(attrs={'class': 'form-control', 'id': 'fiscalia'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'defensoria': forms.TextInput(attrs={'class': 'form-control'}),
            'juzgado': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PericiaForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Pericia

        fields = [
            'proyecto',
            'descripcion',
            'nombrePerito',
            'fecha',
            'tipoPericia',
        ]

        labels = {
            'proyecto': 'Proyecto',
            'descripcion': 'Descripcion',
            'nombrePerito': 'Nombre perito',
            'fecha': 'Fecha',
            'tipoPericia': 'Tipo Pericia',
        }

        widgets = {
            'proyecto': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'id': 'descripcion'}),
            'nombrePerito': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.TextInput(attrs={'class': 'form-control'}),
            'tipoPericia': forms.Select(attrs={'class': 'form-control'}),
        }


class ImagenForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Imagen

        fields = [
            'tipoImagen',
        ]

        labels = {
            'tipoImagen':'Tipo de imagen',
        }

        widgets = {
            'tipoImagen': forms.Select(attrs={'class': 'form-control'}),
        }


class ImagenEditForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Imagen

        fields = [
            'nombre',
            'extension',
            'tipoImagen',
        ]

        labels = {
            'nombre': 'Nombre',
            'extension': 'Extensión',
            'tipoImagen':'Tipo de imagen',
        }

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'id': 'nombre', 'readonly':'readonly'}),
            'extension': forms.TextInput(attrs={'class': 'form-control', 'id': 'extension', 'readonly':'readonly'}),
            'tipoImagen': forms.Select(attrs={'class': 'form-control', 'id': 'tipoImagen'}),
        }