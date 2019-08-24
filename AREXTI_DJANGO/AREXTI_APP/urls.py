from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='arextiIndex'),
    path('ProyectoListar/', views.ProyectoListar.as_view(), name='ProyectoListar'),
    path('ProyectoCrear/', views.ProyectoCrear.as_view(), name='ProyectoCrear'),
    path('ProyectoEditar/<int:pk>/', views.ProyectoEditar.as_view(), name='ProyectoEditar'),
    path('ProyectoEliminar/<int:Proyectoid>/', views.ProyectoEliminar, name='ProyectoEliminar'),
    path('PericiaListar/', views.PericiaListar.as_view(), name='PericiaListar'),
    path('PericiaCrear/', views.PericiaCrear.as_view(), name='PericiaCrear'),
    path('PericiaEditar/<int:pk>/', views.PericiaEditar.as_view(), name='PericiaEditar'),
    path('PericiaEliminar/<int:Periciaid>/', views.PericiaEliminar, name='PericiaEliminar'),

    path('ProyectoListarMarian/', views.ProyectoListarMarian.as_view(), name='ProyectoListarMarian'),
    path('PericiaListarMarian/', views.PericiaListarMarian.as_view(), name='PericiaListarMarian'),
]
