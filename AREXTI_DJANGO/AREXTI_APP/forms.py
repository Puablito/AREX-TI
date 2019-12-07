from django import forms
from AREXTI_APP.models import Proyecto, Pericia, Imagen, TipoImagen, UploadFile


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
            'descripcion': 'Descripción',
            'fiscalia': 'Fiscalía',
            'responsable': 'Responsable',
            'defensoria': 'Defensoría',
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
            'descripcion': 'Descripción',
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


class ProyectoConsultaForm(forms.ModelForm):

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

    def __init__(self, *args, **kwargs):
        super(ProyectoConsultaForm, self).__init__(*args, **kwargs)
        self.fields['IPP'].widget.attrs['readonly'] = True
        self.fields['descripcion'].widget.attrs['readonly'] = True
        self.fields['fiscalia'].widget.attrs['readonly'] = True
        self.fields['responsable'].widget.attrs['readonly'] = True
        self.fields['defensoria'].widget.attrs['readonly'] = True
        self.fields['juzgado'].widget.attrs['readonly'] = True


class PericiaConsultaForm(forms.ModelForm):

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
            'descripcion': 'Descripción',
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

    def __init__(self, *args, **kwargs):
        super(PericiaConsultaForm, self).__init__(*args, **kwargs)
        self.fields['proyecto'].widget.attrs['readonly'] = True
        self.fields['proyecto'].widget.attrs['disabled'] = True
        self.fields['descripcion'].widget.attrs['readonly'] = True
        self.fields['nombrePerito'].widget.attrs['readonly'] = True
        self.fields['fecha'].widget.attrs['readonly'] = True
        self.fields['fecha'].widget.attrs['disabled'] = True
        self.fields['tipoPericia'].widget.attrs['readonly'] = True
        self.fields['tipoPericia'].widget.attrs['disabled'] = True


class ImagenConsultarForm(forms.ModelForm):

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
            'tipoImagen': forms.Select(attrs={'class': 'form-control', 'id': 'tipoImagen', 'readonly':'readonly', 'disabled':True}),
        }

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = ('file',)
