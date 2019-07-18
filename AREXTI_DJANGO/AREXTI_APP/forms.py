from django import forms
from AREXTI_APP.models import Proyecto
class ProyectoForm(forms.ModelForm):

    class Meta:
        model = Proyecto

        fields = [
            'IPP',
            'descripcion',
            # 'fecha',
            'fiscalia',
            'responsable',
            'defensoria',
            'juzgado',
        ]

        labels = {
            'IPP':'IPP',
            'descripcion':'Descripcion',
            # 'fecha':'Fecha',
            'fiscalia':'Fiscalia',
            'responsable':'Responsable',
            'defensoria': 'Defensoria',
            'juzgado': 'Juzgado',
        }

        widgets = {
            'IPP': forms.TextInput(attrs={'class': 'form-control', 'id':'IPP'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            # 'fecha': forms.DateField(),
            'fiscalia': forms.TextInput(attrs={'class': 'form-control', 'id':'fiscalia'}),
            'responsable': forms.TextInput(attrs={'class':'form-control'}),
            'defensoria': forms.TextInput(attrs={'class': 'form-control'}),
            'juzgado': forms.TextInput(attrs={'class': 'form-control'}),
        }