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
from .forms import ProyectoForm, PericiaForm, ImagenForm, ImagenEditForm, ProyectoConsultaForm, PericiaConsultaForm, \
    ImagenConsultarForm, UploadFileForm
from .filters import ProyectoFilter, PericiaFilter, ImagenFilter, ReporteFilter
from . import funcionesdb
import numpy as np
from PIL import Image
from wordcloud import STOPWORDS, WordCloud
import matplotlib.pyplot as plt
import io
import urllib, base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import date, datetime
import locale
from reportlab.lib.pagesizes import A4
import itertools
from random import randint
from statistics import mean

# enumerables
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

    def form_valid(self, form, ):
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

    def form_valid(self, form, ):
        return redirect(self.success_url)


class PericiaListar(FilteredListView):
    filterset_class = PericiaFilter

    def get_queryset(self):
        proid = self.kwargs.get("Proyectoid")
        if proid is None:
            proid = 0
        # queryset = super().get_queryset()
        if proid != 0:
            queryset = Pericia.objects.filter(activo=1, proyecto=proid).annotate(num_imagenes=Count('imagen')).order_by(
                '-proyecto', '-id')
        else:
            queryset = Pericia.objects.filter(activo=1).annotate(num_imagenes=Count('imagen')).order_by('-proyecto',
                                                                                                        '-id')
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

    # Agrego al contexto la periciaId sobre el cual se obtuvo el conjunto de imagenes
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
                'periciaId': pericia.id,  # ver de pasarle el fromTab para setear el mismo
            }
            return render(request, self.template_name, contexto)

        if fromTab == CreateTabs.Directorio.value:
            call_ProcessImage(perid, pericia.descripcion, fromTab, url, hashesId)
        else:
            call_ProcessImage(perid, pericia.descripcion, fromTab, pericia.directorio, hashesId)

        messages.success(self.request, 'Exito en la operacion', extra_tags='title')
        messages.success(self.request, 'Inicia el procesamiento automatico de las imagenes')

        return render(request, 'AREXTI_APP/ImagenListar.html',
                      {'pericia': pericia, 'periciaId': perid})  # deberia llamar al imagenListar


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
        tipoImagenId = request.POST.get('tipoImagen', None)
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

        call_ChangeImageType.delay(imagen.id, imagen.nombre, tipoImagenId)

        messages.success(self.request, 'Exito en la operacion', extra_tags='title')
        messages.success(self.request, 'Inicia el procesamiento automatico de las imagenes')

        return render(request, 'AREXTI_APP/ImagenListar.html',
                      {'pericia': imagen.pericia, 'periciaId': imagen.pericia.id})


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

    def get(self, request, *args, **kwargs):
        if 'reporte' in self.request.GET:
            if self.request.GET['reporte'] == 'xls':
                # self.request.path = '/export/xls/'
                return export_imagenes_xls(self.request)
            if self.request.GET['reporte'] == 'pdf':
                # self.request.path = 'export/pdf/'
                return write_pdf_view(self.request)
        else:
            return super().get(request, *args, **kwargs)

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

    # def get(self, request, *args, **kwargs):
    #     parametros = obtenerParametros(self.request)
    #     palabras = funcionesdb.consulta('nube', [parametros['pericia'], parametros['tiposfinal'],
    #                                              parametros['detallesfinal'], parametros['metadato'],
    #                                              parametros['valormetadato']])
    #     palabrasfinal = []
    #     for palabra in palabras:
    #         palabrasfinal.append([palabra['palabra'], str(palabra['total'])])
    #     # context['nube'] = palabrasfinal
    #     contexto = {
    #         'nube': palabrasfinal,
    #
    #     }
    #
    #     return render(request, self.template_name, contexto)


    def get_queryset(self):
        queryset = None
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)

        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipoHashes'] = TipoHash.objects.filter(activo=1)
        parametros = obtenerParametros(self.request)
        palabras = funcionesdb.consulta('nube', [parametros['pericia'], parametros['tiposfinal'],
                                                        parametros['detallesfinal'], parametros['metadato'],
                                                        parametros['valormetadato']])
        palabrasfinal = []
        for palabra in palabras:
            palabrasfinal.append([palabra['palabra'], str(palabra['total'])])
        context['nube'] = palabrasfinal
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
            # data = {'is_valid': True, 'media': perid}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


def export_imagenes_xls(request):
    params = obtenerParametros(request)

    resultados = funcionesdb.consulta('ocurrencias', [params['palabra'], params['pericia'], params['tiposfinal'],
                                                      params['detallesfinal'], params['metadato'],
                                                      params['valormetadato']], False)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Reporte Ocurrencias "' + params['fechaHora'] + '".xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Imágenes')

    # Sheet header, first row
    row_num = 0

    font_style_cabecera = xlwt.XFStyle()
    font_style_cabecera.font.bold = True
    font_style_cabecera.font.height = 280
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['gray25']
    font_style_cabecera.pattern = pattern

    columns = ['Id', '', 'Tipo Imagen', '', 'Nombre', '', 'Extensión', '', 'Hash MD5', '', 'Hash SHA1', '',
               'Hash SHA256', '', 'Ocurrencias']
    ws.write_merge(row_num, row_num + 1, 0, 3, 'Fecha: ' + params['fechacompleta'], font_style_cabecera)
    ws.write_merge(row_num + 2, row_num + 3, 0, 3, 'Pericia: ' + params['pericia'] + ' - ' + params['periciaNombre'], font_style_cabecera)
    ws.write_merge(row_num + 2, row_num + 3, 4, 6, 'Palabra: ' + params['palabra'], font_style_cabecera)
    if resultados:
        total_ocu = str(resultados[0][8])
    else:
        total_ocu = ''
    ws.write_merge(row_num + 2, row_num + 3, 7, 9, 'Total Ocurrencias: ' + total_ocu, font_style_cabecera)
    row_num = 5
    font_style_titulos = xlwt.XFStyle()
    font_style_titulos.font.bold = True
    font_style_titulos.font.height = 240
    font_style_titulos.alignment.horz = xlwt.Alignment.HORZ_CENTER
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['gray25']
    font_style_titulos.pattern = pattern
    for col_num in range(len(columns)):
        if (col_num % 2) == 0:
            ws.write_merge(row_num, row_num, col_num, col_num + 1, columns[col_num], font_style_titulos)
    if resultados:
        # Sheet body, remaining rows
        font_style_detalles = xlwt.XFStyle()
        font_style_detalles.alignment.horz = xlwt.Alignment.HORZ_CENTER
        font_style_detalles.font.height = 220
        if len(resultados) > 1:
            for imagen in resultados:
                row_num += 1
                for col_num in range(len(imagen) - 1):
                    ws.write_merge(row_num, row_num, col_num * 2, col_num * 2 + 1, imagen[col_num], font_style_detalles)
        else:
            row_num += 1
            for col_num in range(len(resultados[0]) - 1):
                ws.write_merge(row_num, row_num, col_num * 2, col_num * 2 + 1, resultados[0][col_num], font_style_detalles)
    else:
        ws.write_merge(10, 11, 0, 4, 'No se encontraron coincidencias', font_style_titulos)
    wb.save(response)
    return response


def grouper(iterable, n):
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args)


def write_pdf_view(request):
    params = obtenerParametros(request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Reporte Ocurrencias "' + params['fechaHora'] + '".pdf"'
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    imagenes = funcionesdb.consulta('ocurrencias', [params['palabra'], params['pericia'], params['tiposfinal'],
                                                    params['detallesfinal'], params['metadato'], params['valormetadato']])

    logo = 'C:/Users/Mariano-Dell/Desktop/Tesis/Logo2.jpg'
    w, h = letter
    max_rows_per_page = 30
    # Margenes.
    x_offset = 50
    y_offset = 150
    # Espacio entre filas.
    padding = 20
    # p.drawImage(archivo_imagen, 20, h - 300, 300, 300, preserveAspectRatio=True)
    p.drawImage(logo, 40, h - 100, width=100, height=75, preserveAspectRatio=True)
    texto = p.beginText(150, h - 55)
    # texto.setFont("Times-Roman", 16)
    texto.textLine("Fecha: " + params['fechacompleta'])
    texto.textLine("Pericia: " + params['pericia'] + ' - ' + params['periciaNombre'])
    texto.textLine("Palabra: " + params['palabra'])
    if imagenes:
        total_ocu = str(imagenes[0]['suma_total_ocu'])
    else:
        total_ocu = ''
    texto.textLine("Total Ocurrencias: " + total_ocu)
    p.drawText(texto)
    xlist = [x + x_offset for x in [0, 50, 130, 370, 430, 500]]
    ylist = [h - y_offset - i * padding for i in range(max_rows_per_page + 1)]

    data = [('Id', 'Tipo Imagen', 'Nombre', 'Extensión', 'Ocurrencias')]
    if imagenes:
        for imagen in imagenes:
            data.append((str(imagen['imagenid']), imagen['tipoImagen_id'], imagen['nombre'], imagen['extension'],
                        str(imagen['total_ocurrencias'])))
        for rows in grouper(data, max_rows_per_page):
            rows = tuple(filter(bool, rows))
            p.grid(xlist, ylist[:len(rows) + 1])
            for y, row in zip(ylist[:-1], rows):
                for x, cell in zip(xlist, row):
                    nombre = str(cell)
                    if len(nombre) > 32:
                        nombre = nombre[0:32] + '...'
                    p.drawString(x + 2, y - padding + 3, nombre)
            p.showPage()
        p.save()
    else:
        p.drawString(52, 622 - padding + 3, 'No se encontraron coincidencias')
        p.showPage()
        p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response


def obtenerParametros(request):
    locale.setlocale(locale.LC_TIME, '')
    fecha = datetime.now()
    parametros = dict(request.GET)
    pericia = 0
    pericianombre = ''
    if 'pericia' in parametros:
        pericia = parametros['pericia'][0]
        pericianombre = Pericia.objects.filter(id=pericia)[0].descripcion
    tiposfinal = ''
    if 'tipoImagen' in parametros:
        tipos = parametros['tipoImagen']
        for tipo in tipos:
            tiposfinal += tipo + '.'
    detallesfinal = ''
    if 'tipoDetalle' in parametros:
        detalles = parametros['tipoDetalle']
        for detalle in detalles:
            detallesfinal += detalle + '.'
    texto = ''
    if 'texto' in parametros:
        texto = parametros['texto'][0]

    metadato = ''
    if 'metadato' in parametros:
        texto = parametros['metadato'][0]
    valormeta = ''
    if 'valormeta' in parametros:
        valormeta = parametros['valormeta'][0]

    parametrosfinal = {'fechacompleta': fecha.strftime("%d " + "de " + "%B, %Y"),
                       'fechaHora': fecha.strftime("%d_%m_%Y_%H%M%S"),
                       'palabra': texto,
                       'pericia': pericia,
                       'tiposfinal': tiposfinal,
                       'detallesfinal': detallesfinal,
                       'metadato':metadato,
                       'valormetadato': valormeta,
                       'periciaNombre': pericianombre
                       }
    return parametrosfinal


def word_cloud(text):
    # whale_mask = np.array(Image.open("PK_t.png"))
    stopwords = {'은', '입니다'}
    plt.figure(figsize=(20, 5))
    # plt.imshow(whale_mask , cmap = plt.cm.gray , interpolation = 'bilinear')
    # font_path = 'C:/Users/Jeong Suji/NanumBarunGothic.ttf'
    wc = WordCloud(background_color='white', max_words=2000,
                   stopwords=stopwords)
    # wc = WordCloud(font_path=font_path, background_color='white', max_words=2000, mask=whale_mask,
    #                stopwords=stopwords)
    wc = wc.generate(text)
    plt.figure(figsize=(10, 5))
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
