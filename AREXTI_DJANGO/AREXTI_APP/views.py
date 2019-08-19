from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from AREXTI_APP.models import Proyecto, Pericia
from AREXTI_APP.forms import ProyectoForm, PericiaForm


def home(request):
    return render(request, 'AREXTI_APP/home.html')


class ProyectoListar(ListView):
    # model = Proyecto
    context_object_name = 'proyecto_lista'
    queryset = Proyecto.objects.filter(activo=1)
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


# class ProyectoEliminar():
#     model = Proyecto
#     template_name = 'AREXTI_APP/ProyectoListar.html'
#     success_url = reverse_lazy('ProyectoListar')


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

class PericiaListar(ListView):
    # model = Pericia
    context_object_name = 'pericia_lista'
    queryset = Pericia.objects.filter(activo=1)
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