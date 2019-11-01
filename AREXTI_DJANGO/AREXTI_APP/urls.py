from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='arextiIndex'),
    path('ProyectoListar/', views.ProyectoListar.as_view(), name='ProyectoListar'),
    path('ProyectoCrear/', views.ProyectoCrear.as_view(), name='ProyectoCrear'),
    path('ProyectoEditar/<int:pk>/', views.ProyectoEditar.as_view(), name='ProyectoEditar'),
    path('ProyectoEliminar/<int:Proyectoid>/', views.ProyectoEliminar, name='ProyectoEliminar'),
    path('PericiaListar/<int:Proyectoid>/', views.PericiaListar.as_view(), name='PericiaListar'),
    path('PericiaCrear/', views.PericiaCrear.as_view(), name='PericiaCrear'),
    path('PericiaEditar/<int:pk>/', views.PericiaEditar.as_view(), name='PericiaEditar'),
    path('PericiaEliminar/<int:Periciaid>/', views.PericiaEliminar, name='PericiaEliminar'),
    path('ImagenListar/<int:pericia>/', views.ImagenListar.as_view(), name='ImagenListar'),
    path('ImagenCrear/<int:pericia>/', views.ImagenCrear.as_view(), name='ImagenCrear'),
    path('ImagenEditar/<int:pk>/', views.ImagenEditar.as_view(), name='ImagenEditar'),
    path('ImagenEliminar/<int:Imagenid>/', views.ImagenEliminar, name='ImagenEliminar'),
]
