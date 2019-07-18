from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
import json
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from AREXTI_APP.models import Proyecto
from AREXTI_APP.forms import ProyectoForm


def home(request):
    return render(request, 'AREXTI_APP/home.html')


class ProyectoListar(ListView):
    model = Proyecto
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
class ProyectoEliminar(DeleteView):
    model = Proyecto
    template_name = 'AREXTI_APP/ProyectoListar.html'
    success_url = reverse_lazy('ProyectoListar')