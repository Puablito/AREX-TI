from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import ListView, CreateView, UpdateView
from AREXTI_APP.models import Proyecto, Pericia, Imagen, TipoHash, ImagenHash
from AREXTI_APP.forms import ProyectoForm, PericiaForm, ImagenForm
from .filters import ProyectoFilter, PericiaFilter
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# from django_filters import FilterView


class FilteredListView(ListView):
    filterset_class = None

    def get_queryset(self):
        # Get the queryset however you usually would.  For example:
        queryset = super().get_queryset()
        # Then use the query parameters and the queryset to
        # instantiate a filterset and save it as an attribute
        # on the view instance for later.
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        # Return the filtered queryset
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the filterset to the template - it provides the form.
        context['filterset'] = self.filterset
        return context


def home(request):
    return render(request, 'home/index.html')


# class ProyectoListarOld(ListView):
#     # model = Proyecto
#     context_object_name = 'proyecto_lista'
#     paginate_by = 5
#     queryset = Proyecto.objects.filter(activo=1)
#     template_name = 'AREXTI_APP/ProyectoListar.html'

class ProyectoListar(FilteredListView):
    filterset_class = ProyectoFilter
    queryset = Proyecto.objects.filter(activo=1).order_by('-id')
    paginate_by = 5
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
        pro = Proyecto.objects.get(id=Proyectoid)
        pro.activo = 0
        pro.save()
    return redirect('ProyectoListar')

    # def post(self, *args, **kwargs):
    #     self.object = self.get_object()
    #     self.object.activo = 0
    #     self.object.save(update_fields=('activo', ))
    #     return HttpResponseRedirect('PericiaListar/')


class PericiaListarOld(ListView):
    # model = Pericia
    context_object_name = 'pericia_lista'
    paginate_by = 10
    queryset = Pericia.objects.filter(activo=1)
    template_name = 'AREXTI_APP/PericiaListar.html'


class PericiaListar(FilteredListView):
    filterset_class = PericiaFilter
    queryset = Pericia.objects.filter(activo=1).order_by('-id')
    paginate_by = 5
    template_name = 'AREXTI_APP/PericiaListar.html'


class PericiaCrear(CreateView):
    model = Pericia
    form_class = PericiaForm
    template_name = 'AREXTI_APP/PericiaCrear.html'
    success_url = reverse_lazy('PericiaListar')


class PericiaEditar(UpdateView):
    model = Pericia
    form_class = PericiaForm
    template_name = 'AREXTI_APP/PericiaCrear.html'
    success_url = reverse_lazy('PericiaListar')


def PericiaEliminar(request, Periciaid):
    # model = Proyecto
    if Periciaid:
        pro = Pericia.objects.get(id=Periciaid)
        pro.activo = 0
        pro.save()
    return redirect('PericiaListar')


class ImagenListar(ListView):
    # model = Imagen
    context_object_name = 'imagen_lista'
    queryset = Imagen.objects.filter(activo=1)
    template_name = 'AREXTI_APP/ImagenListar.html'


class ImagenCrear(CreateView):
    model = Imagen
    form_class = ImagenForm
    template_name = 'AREXTI_APP/ImagenCrear.html'
    success_url = reverse_lazy('ImagenListar')


class ImagenEditar(UpdateView):
    model = Imagen
    form_class = ImagenForm
    template_name = 'AREXTI_APP/ImagenEditar.html'
    success_url = reverse_lazy('ImagenListar')


def ImagenEliminar(request, Imagenid):
    if Imagenid:
        img = Imagen.objects.get(id=Imagenid)
        img.activo = 0
        img.save()
    return redirect('ImagenListar')


