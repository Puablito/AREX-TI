from django import forms
from AREXTI_APP.models import Proyecto, Pericia, Imagen


class DateInput(forms.DateInput):
    input_type = 'date'


class ProyectoForm(forms.ModelForm):

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
            'IPP':'IPP',
            'descripcion':'Descripcion',
            'fiscalia':'Fiscalia',
            'responsable':'Responsable',
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
            'fecha': DateInput(attrs={'class': 'form-control'}),
            'tipoPericia': forms.Select(attrs={'class': 'form-control'}),
        }


class ImagenForm(forms.ModelForm):

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