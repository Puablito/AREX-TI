from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from enum import Enum
from .tasks import getDirectories, call_ChangeImageType, call_ProcessImage
import os
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.conf import settings
from django.template import loader
from django.http import HttpResponse, HttpResponseNotFound
from django.core.files.storage import FileSystemStorage
import xlwt
from io import BytesIO
from reportlab.pdfgen import canvas
from django.views.generic import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View, TemplateView
from .models import Proyecto, Pericia, Imagen, TipoHash, ImagenHash, ImagenDetalle, ImagenFile, UploadFile, Parametros
from .forms import ProyectoForm, PericiaForm, ImagenForm, ImagenEditForm, ProyectoConsultaForm, PericiaConsultaForm, ImagenConsultarForm, UploadFileForm
from .filters import ProyectoFilter, PericiaFilter, ImagenFilter, ReporteFilter
from . import funcionesdb
import numpy as np
from PIL import Image
from wordcloud import STOPWORDS, WordCloud
import matplotlib.pyplot as plt
import io
import urllib, base64


#enumerables
class messageTitle(Enum):
    Alta = "Alta exitosa"
    Modificacion = "Modificación exitosa"


class CreateTabs(Enum):
    Directorio = "D"
    Archivo = "A"


class ParametroSistema(Enum):
    DirectorioBase = "DIRECTORIOIMAGEN"

class FilteredListView(ListView):
    filterset_class = None
    idfil = 0
    def get_queryset(self):
        # Get the queryset however you usually would.  For example:
        queryset = super().get_queryset()
        # Then use the query parameters and the queryset to
        # instantiate a filterset and save it as an attribute
        # on the view instance for later.

        # self.idfil = self.extra_context['id']
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        # Return the filtered queryset
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the filterset to the template - it provides the form.
        context['filterset'] = self.filterset
        return context


class Home(TemplateView):
    template_name = 'home/index.html'


class ProyectoListar(FilteredListView):
    filterset_class = ProyectoFilter
    queryset = Proyecto.objects.filter(activo=1).order_by('-id')


    def get_paginate_by(self, queryset):
        paginacion = self.request.GET.get('paginate_by', self.paginate_by)
        if paginacion:
            return paginacion
        else:
            return 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['numero_paginacion'] = self.kwargs.get('paginate_by')
        paginacion = self.request.GET.get('paginate_by')
        if paginacion == None:
            paginacion = 5
        context['numero_paginacion'] = int(paginacion)
        # self.paginate_by = paginacion
        return context

    template_name = 'AREXTI_APP/ProyectoListar.html'


class ProyectoCrear(CreateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'AREXTI_APP/ProyectoCrear.html'
    success_url = reverse_lazy('ProyectoListar')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, messageTitle.Alta.value, extra_tags='title')
        return redirect(self.success_url)

    def form_invalid(self, form):
        ctx = {'form': form}
        return render(self.request, self.template_name, ctx)


class ProyectoEditar(UpdateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'AREXTI_APP/ProyectoCrear.html'
    success_url = reverse_lazy('ProyectoListar')

    def form_valid(self, form,):
        form.save()
        messages.success(self.request, messageTitle.Modificacion.value, extra_tags='title')
        return redirect(self.success_url)

    def form_invalid(self, form):
        ctx = {'form': form}
        return render(self.request, self.template_name, ctx)


def ProyectoEliminar(request, Proyectoid):
    # model = Proyecto
    if Proyectoid:
        # PRIMERO ELIMINACION LOGICA DE PERICIAS E IMAGENES CORRESPONDIENTES AL PROYECTO
        pericias = Pericia.objects.filter(proyecto=Proyectoid)
        for per in pericias:
            imagenes = Imagen.objects.filter(pericia=per.id)
            for ima in imagenes:
                ima.activo = 0
                ima.save()
            per.activo = 0
            per.save()
        pro = Proyecto.objects.get(id=Proyectoid)
        pro.activo = 0
        pro.save()
    return redirect('ProyectoListar')


class ProyectoConsultar(UpdateView):
    model = Proyecto
    form_class = ProyectoConsultaForm
    template_name = 'AREXTI_APP/ProyectoCrear.html'
    success_url = reverse_lazy('ProyectoListar')

    def form_valid(self, form,):
        return redirect(self.success_url)


class PericiaListar(FilteredListView):
    filterset_class = PericiaFilter

    def get_queryset(self):
        proid = self.kwargs.get("Proyectoid")
        if proid is None:
            proid = 0
        # queryset = super().get_queryset()
        if proid != 0:
            queryset = Pericia.objects.filter(activo=1, proyecto=proid).annotate(num_imagenes=Count('imagen')).order_by('-proyecto', '-id')
        else:
            queryset = Pericia.objects.filter(activo=1).annotate(num_imagenes=Count('imagen')).order_by('-proyecto', '-id')
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)

        return self.filterset.qs.distinct()

    def get_paginate_by(self, queryset):
        paginacion = self.request.GET.get('paginate_by', self.paginate_by)
        if paginacion:
            return paginacion
        else:
            return 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proid = self.kwargs.get("Proyectoid")
        if proid is None:
            proid = 0
        context['proyectoId'] = proid
        paginacion = self.request.GET.get('paginate_by')
        if paginacion == None:
            paginacion = 5
        context['numero_paginacion'] = int(paginacion)
        return context

    template_name = 'AREXTI_APP/PericiaListar.html'


class PericiaCrear(CreateView):
    model = Pericia
    form_class = PericiaForm
    template_name = 'AREXTI_APP/PericiaCrear.html'
    pericia = None

    def form_valid(self, form):
        self.pericia = form.save()
        messages.success(self.request, messageTitle.Alta.value, extra_tags='title')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        ctx = {'form': form}
        return render(self.request, self.template_name, ctx)

    def get_success_url(self):
        return reverse_lazy('PericiaListar', kwargs={'Proyectoid': self.pericia.proyecto.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proid = self.kwargs.get("Proyectoid")
        if proid is None:
            proid = 0
        context['proyectoId'] = proid
        return context


class PericiaEditar(UpdateView):
    model = Pericia
    form_class = PericiaForm
    template_name = 'AREXTI_APP/PericiaCrear.html'

    def form_valid(self, form):
        form.save()
        messages.success(self.request, messageTitle.Modificacion.value, extra_tags='title')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.warning(self.request, 'Por favor corrija los errores')
        ctx = {'form': form}
        return render(self.request, self.template_name, ctx)

    def get_success_url(self):
        return reverse_lazy('PericiaListar', kwargs={'Proyectoid': self.object.proyecto.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proid = self.kwargs.get("Proyectoid")
        if proid is None:
            proid = 0
        context['proyectoId'] = proid
        return context


def PericiaEliminar(request, Periciaid):
    # model = Proyecto
    if Periciaid:
        # PRIMERO ELIMINACION LOGICA DE IMAGENES CORRESPONDIENTES A LA PERICIA
        imagenes = Imagen.objects.filter(pericia=Periciaid)
        for ima in imagenes:
            ima.activo = 0
            ima.save()
        per = Pericia.objects.get(id=Periciaid)
        per.activo = 0
        per.save()
        pro = per.proyecto.id
    return redirect('PericiaListar', Proyectoid=pro)


class PericiaConsultar(UpdateView):
    model = Pericia
    form_class = PericiaConsultaForm
    template_name = 'AREXTI_APP/PericiaCrear.html'

    def form_valid(self, form, ):
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('PericiaListar', kwargs={'Proyectoid': self.object.proyecto.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proid = self.kwargs.get("Proyectoid")
        if proid is None:
            proid = 0
        context['proyectoId'] = proid
        return context


class ImagenListar(FilteredListView):
    filterset_class = ImagenFilter

    def get_queryset(self):
        perid = self.kwargs.get("pericia")
        # queryset = super().get_queryset()
        if perid != 0:
            queryset = Imagen.objects.filter(activo=1, pericia=perid).order_by('-id')
        else:
            queryset = Imagen.objects.filter(activo=1).order_by('-id')
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)

        return self.filterset.qs.distinct()
    # queryset = Imagen.objects.filter(activo=1).order_by('-id')

    def get_paginate_by(self, queryset):
        paginacion = self.request.GET.get('paginate_by', self.paginate_by)
        if paginacion:
            return paginacion
        else:
            return 5

    #Agrego al contexto la periciaId sobre el cual se obtuvo el conjunto de imagenes
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periciaId = self.kwargs.get("pericia")
        context['periciaId'] = periciaId
        context['tipoHashes'] = TipoHash.objects.filter(activo=1)
        context['pericia'] = Pericia.objects.get(pk=periciaId)

        paginacion = self.request.GET.get('paginate_by')
        if paginacion == None:
            paginacion = 5
        context['numero_paginacion'] = int(paginacion)

        return context

    paginate_by = 10
    template_name = 'AREXTI_APP/ImagenListar.html'


class ImagenCrear(CreateView):
    model = ImagenFile
    template_name = 'AREXTI_APP/ImagenCrear.html'

    def get(self, request, *args, **kwargs):
        queryset = TipoHash.objects.filter(activo=1)
        activeTab = False

        perid = self.kwargs.get("pericia")

        if Imagen.objects.filter(pericia=perid).count() > 0:
            activeTab = True

        pericia = get_object_or_404(Pericia, pk=perid)

        photos_list = UploadFile.objects.filter(periciaId=perid)
        directorioBase = Parametros.objects.get(id=ParametroSistema.DirectorioBase.value)

        path = os.path.join(directorioBase.valorTexto, pericia.directorio)
        directorios = getDirectories(path, "", 1)
        contexto = {
            'tipoHashes': queryset,
            'activeTab': activeTab,
            'directorios': directorios,
            'periciaId': pericia.id,
            'photos': photos_list,
            'archivoTab': "A",
            'directorioTab': "D",
        }

        return render(request, self.template_name, contexto)

    def post(self, request, *args, **kwargs):
        hashesDirectorioId = request.POST.getlist('inputHashDirectorio')
        hashesArchivoId = request.POST.getlist('inputHashArchivo')
        perid = self.kwargs.get("pericia")
        url = request.POST.get('urlFile', None)
        fromTab = request.POST.get('fromTab', None)
        pericia = get_object_or_404(Pericia, pk=perid)

        isValid = True
        stringList = list()

        if not fromTab or fromTab not in [CreateTabs.Archivo.value, CreateTabs.Directorio.value]:
            isValid = False
            stringList.append('Debe seleccionar una opcion para cargar imagenes')

        if not perid or perid == 0:
            isValid = False
            stringList.append('Debe existir una pericia para operar')

        if fromTab == CreateTabs.Directorio.value and not url:
            isValid = False
            stringList.append('Seleccione un directorio de cual se extraeran las imagenes')

        if fromTab == CreateTabs.Directorio.value and not hashesDirectorioId:
            isValid = False
            stringList.append('Seleccione uno o mas hashes para aplicar a las imagenes del directorio')

        if fromTab == CreateTabs.Archivo.value and not hashesArchivoId:
            isValid = False
            stringList.append('Seleccione uno o mas hashes para aplicar a los archivos')

        if not isValid:
            messages.error(self.request, 'Por favor corrija los errores', extra_tags='title')

            for st in stringList:
                messages.error(self.request, st)

            queryset = TipoHash.objects.filter(activo=1)
            activeTab = False
            if Imagen.objects.filter(pericia=perid).count() > 0:
                activeTab = True

            directorioBase = Parametros.objects.get(id=ParametroSistema.DirectorioBase.value)

            path = os.path.join(directorioBase.valorTexto, pericia.directorio)
            directorios = getDirectories(path, "", 1)
            contexto = {
                'tipoHashes': queryset,
                'activeTab': activeTab,
                'directorios': directorios,
                'periciaId': pericia.id,  #ver de pasarle el fromTab para setear el mismo
            }
            return render(request, self.template_name, contexto)

        if fromTab == CreateTabs.Directorio.value:
            call_ProcessImage(perid, pericia.descripcion, fromTab, url, hashesId)
        else:
            call_ProcessImage(perid, pericia.descripcion, fromTab, pericia.directorio, hashesId)

        messages.success(self.request, 'Exito en la operacion', extra_tags='title')
        messages.success(self.request, 'Inicia el procesamiento automatico de las imagenes')

        return render(request, 'AREXTI_APP/ImagenListar.html', {'pericia': pericia, 'periciaId': perid}) #deberia llamar al imagenListar


class ImagenEditar(UpdateView):
    model = Imagen
    form_class = ImagenEditForm
    template_name = 'AREXTI_APP/ImagenEditar.html'

    def get_context_data(self, *args, **kwargs):
        imagen = self.get_object()
        context = super().get_context_data(*args, **kwargs)
        context['detalles'] = ImagenDetalle.objects.filter(imagen=imagen).order_by('id')
        context['periciaId'] = imagen.pericia.id
        return context

    def post(self, request, *args, **kwargs):
        tipoImagenId = request.POST.get('TipoImagen', None)
        imagen = self.get_object()

        isValid = True
        stringList = list()

        if not tipoImagenId:
            isValid = False
            stringList.append('Seleccione el tipo de imagen al que quiere cambiar')

        if not isValid:
            messages.error(self.request, 'Por favor corrija los errores', extra_tags='title')

            for st in stringList:
                messages.error(self.request, st)

            return render(request, self.template_name, {'imagen': imagen, 'periciaId': imagen.pericia.id})

        call_ChangeImageType(imagen.id, imagen.nombre, tipoImagenId)

        messages.success(self.request, 'Exito en la operacion', extra_tags='title')
        messages.success(self.request, 'Inicia el procesamiento automatico de las imagenes')

        return render(request, 'AREXTI_APP/ImagenListar.html', {'pericia': imagen.pericia, 'periciaId': imagen.pericia.id})


class ImagenConsultar(UpdateView):
    model = Imagen
    form_class = ImagenConsultarForm
    template_name = 'AREXTI_APP/ImagenEditar.html'

    def get_context_data(self, *args, **kwargs):
        imagen = self.get_object()
        context = super().get_context_data(*args, **kwargs)
        context['detalles'] = ImagenDetalle.objects.filter(imagen=imagen).order_by('id')
        context['periciaId'] = imagen.pericia.id
        return context

    # def get_success_url(self):
    #     print(self.kwargs)
    #     return reverse('ImagenListar', kwargs={'pericia': 5})


def ImagenEliminar(request, Imagenid):
    if Imagenid:
        img = Imagen.objects.get(id=Imagenid)
        img.activo = 0
        img.save()
    return redirect('ImagenListar', img.pericia.id)


class ReporteOcurrencia(FilteredListView):
    filterset_class = ReporteFilter

    def get_paginate_by(self, queryset):
        paginacion = self.request.GET.get('paginate_by', self.paginate_by)
        if paginacion:
            return paginacion
        else:
            return 5

    def get_queryset(self):
        queryset = None
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)

        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipoHashes'] = TipoHash.objects.filter(activo=1)
        paginacion = self.request.GET.get('paginate_by')
        if paginacion == None:
            paginacion = 5
        context['numero_paginacion'] = int(paginacion)
        return context

    template_name = 'AREXTI_APP/ReporteOcurrencia.html'


class ReporteNube(FilteredListView):
    filterset_class = ReporteFilter

    def get_queryset(self):
        queryset = None
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)

        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipoHashes'] = TipoHash.objects.filter(activo=1)
        return context

    template_name = 'AREXTI_APP/ReporteNube.html'


class BasicUploadView(View):
    def get(self, request, *args, **kwargs):
        perid = self.kwargs.get("pericia")
        photos_list = UploadFile.objects.filter(periciaId=perid)
        return render(self.request, 'ImagenCrear.html', {'photos': photos_list})
        # return render(self.request, 'files/basic_upload/index.html', {'photos': photos_list})

    def post(self, request, *args, **kwargs):
        form = UploadFileForm(self.request.POST, self.request.FILES)
        perid = self.kwargs.get("pericia")
        if form.is_valid():
            uploadFile = form.save(commit=False)
            uploadFile.periciaId = perid
            uploadFile.save()

            data = {'is_valid': True, 'name': uploadFile.file.name, 'url': uploadFile.file.url}
            #data = {'is_valid': True, 'media': perid}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


def export_imagenes_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Ocurrencias por palabra.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Imagenes')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['pericia', 'tipoImagen', 'nombre', 'extension']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    palabra = 'pablito'
    pericia = 1
    tiposfinal = ''
    detallesfinal = ''
    metadato = ''
    valormetadato = ''
    rows = funcionesdb.consulta('ocurrencias', [palabra, pericia, tiposfinal, detallesfinal, metadato, valormetadato])
    rows = Imagen.objects.all().values_list('pericia', 'tipoImagen', 'nombre', 'extension')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


def write_pdf_view(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    palabra = 'pablito'
    pericia = 1
    tiposfinal = ''
    detallesfinal = ''
    metadato = ''
    valormetadato = ''
    rows = funcionesdb.consulta('ocurrencias', [palabra, pericia, tiposfinal, detallesfinal, metadato, valormetadato])
    # Start writing the PDF here
    linea = 0
    for fila in rows:
        p.drawString(10, linea, str(fila['total_ocurrencias']) + ' ' + fila['nombre'] + ' ' + fila['extension'] + ' ' + fila['tipoImagen_id'] + ' ')
        linea += 50
    # End writing

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response

def word_cloud(text):
    # whale_mask = np.array(Image.open("PK_t.png"))
    stopwords ={'은','입니다'}
    plt.figure(figsize = (20,5))
    #plt.imshow(whale_mask , cmap = plt.cm.gray , interpolation = 'bilinear')
    # font_path = 'C:/Users/Jeong Suji/NanumBarunGothic.ttf'
    wc = WordCloud(background_color = 'white', max_words=2000,
              stopwords = stopwords)
    # wc = WordCloud(font_path=font_path, background_color='white', max_words=2000, mask=whale_mask,
    #                stopwords=stopwords)
    wc= wc.generate(text)
    plt.figure(figsize= (10,5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")

    image = io.BytesIO()
    plt.savefig(image, format='png')
    image.seek(0)  # rewind the data
    string = base64.b64encode(image.read())

    image_64 = 'data:image/png;base64,' + urllib.parse.quote(string)
    return image_64

def cloud_gen(request):
    text = ''
    for i in ImagenDetalle.objects.all():
        text += i.texto
    wordcloud = word_cloud(text)
    return render(request, 'ReporteNube.html', {'wordcloud': wordcloud})
