from django.shortcuts import render, redirect
import logging
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse

from django.template import loader

from django.views.generic import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from AREXTI_APP.models import Proyecto, Pericia, Imagen, TipoHash, ImagenHash, ImagenDetalle, ImagenFile
from AREXTI_APP.forms import ProyectoForm, PericiaForm, ImagenForm, ImagenEditForm
from .filters import ProyectoFilter, PericiaFilter, ImagenFilter

import os
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
import json as simplejson
from django.template import Context, loader
from django.template.context_processors import csrf
import subprocess


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


class ProyectoEditar(UpdateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'AREXTI_APP/ProyectoCrear.html'
    success_url = reverse_lazy('ProyectoListar')


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


class PericiaListar(FilteredListView):
    filterset_class = PericiaFilter

    def get_queryset(self):
        proid = self.kwargs.get("id")
        if proid is None:
            proid = 0
        # queryset = super().get_queryset()
        if proid != 0:
            queryset = Pericia.objects.filter(activo=1, proyecto=proid).order_by('-proyecto', '-id')
        else:
            queryset = Pericia.objects.filter(activo=1).order_by('-proyecto', '-id')
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
        context['proyectoId'] = self.kwargs.get("id")
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
    success_url = reverse_lazy('PericiaListar', kwargs={'id': 0})  # PASAR ID DE PERICIA EN LISTADO


class PericiaEditar(UpdateView):
    model = Pericia
    form_class = PericiaForm
    template_name = 'AREXTI_APP/PericiaCrear.html'
    def get_success_url(self):
        print(self.kwargs)
        return reverse_lazy('PericiaListar', kwargs={'id': self.model.proyecto}) # VER NO FUNCIONA


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
    return redirect('PericiaListar', id=pro)


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

    #Agrego al contexto la periciaId sobre el cual se obtuvo el conjunto de imagenes
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['periciaId'] = self.kwargs.get("pericia")
        context['tipoHashes'] = TipoHash.objects.filter(activo=1)
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

        contexto = {
            'tipoHashes': queryset,
            'activeTab': activeTab
        }

        return render(request, self.template_name, contexto)

    def post(self, request, *args, **kwargs):
        hashesId = request.POST.getlist('inputHash')
        hashes = TipoHash.objects.filter(id__in=hashesId)
        jsonObject = {}
        hashListObject = []

        for hash in hashes:
            hashObject = {"name": hash.nombre}
            hashListObject.append(hashObject)

        jsonObject["hashes"] = hashListObject
        jsonObject["pericia"] = 1
        jsonObject["urlFile"] = "C:\\Users\\javier\\Desktop\\Capturas"

        return render(request, self.template_name, {'pepe': jsonObject})


# class ImagenCrear(View):
#     model = ImagenFile
#     template_name = 'AREXTI_APP/ImagenCrear.html'
#     success_url = reverse_lazy('ImagenListar', 1)
#
#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(*args, **kwargs)
#         context['tipoHashes'] = TipoHash.objects.filter(activo=1)
#         return context


class ImagenEditar(UpdateView):
    model = Imagen
    form_class = ImagenEditForm
    template_name = 'AREXTI_APP/ImagenEditar.html'

    def get_context_data(self, *args, **kwargs):
        imagen = self.get_object()
        context = super().get_context_data(*args, **kwargs)
        context['detalles'] = ImagenDetalle.objects.filter(imagen=imagen)
        return context

    def get_success_url(self):
        print(self.kwargs)
        return reverse('ImagenListar', kwargs={'id': self.model.pericia})


class ImagenConsultar(DetailView):
    model = Imagen
    template_name = 'AREXTI_APP/ImagenEditar.html'

    def get_context_data(self, *args, **kwargs):
        imagen = self.get_object()
        context = super().get_context_data(*args, **kwargs)
        context['detalles'] = ImagenDetalle.objects.filter(imagen=imagen)
        return context


def ImagenEliminar(request, Imagenid):
    if Imagenid:
        img = Imagen.objects.get(id=Imagenid)
        img.activo = 0
        img.save()
    return redirect('ImagenListar', img.pericia.id)





