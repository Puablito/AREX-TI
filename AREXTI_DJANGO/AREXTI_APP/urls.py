from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='arextiHome'),
    path('ProyectoListar/', views.ProyectoListar.as_view(), name='ProyectoListar'),
    path('ProyectoCrear/', views.ProyectoCrear.as_view(), name='ProyectoCrear'),
    path('ProyectoEditar/<int:pk>/', views.ProyectoEditar.as_view(), name='ProyectoEditar'),
    path('ProyectoEliminar/<int:pk>/', views.ProyectoEliminar.as_view(), name='ProyectoEliminar'),
]
