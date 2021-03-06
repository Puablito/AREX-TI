from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='arextiIndex'),
    path('ProyectoListar/', views.ProyectoListar.as_view(), name='ProyectoListar'),
    path('ProyectoCrear/', views.ProyectoCrear.as_view(), name='ProyectoCrear'),
    path('ProyectoEditar/<int:pk>/', views.ProyectoEditar.as_view(), name='ProyectoEditar'),
    path('ProyectoEliminar/<int:Proyectoid>/', views.ProyectoEliminar, name='ProyectoEliminar'),
    path('PericiaListar/<int:Proyectoid>/', views.PericiaListar.as_view(), name='PericiaListar'),
    path('PericiaCrear/<int:Proyectoid>/', views.PericiaCrear.as_view(), name='PericiaCrear'),
    path('PericiaEditar/<int:pk>/<int:Proyectoid>/', views.PericiaEditar.as_view(), name='PericiaEditar'),
    path('PericiaEliminar/<int:Periciaid>/<int:Proyectoid>/', views.PericiaEliminar, name='PericiaEliminar'),
    path('ImagenListar/<int:pericia>/', views.ImagenListar.as_view(), name='ImagenListar'),
    path('ImagenCrear/<int:pericia>/', views.ImagenCrear.as_view(), name='ImagenCrear'),
    path('ImagenEditar/<int:pk>/', views.ImagenEditar.as_view(), name='ImagenEditar'),
    path('ImagenEliminar/<int:Imagenid>/', views.ImagenEliminar, name='ImagenEliminar'),
    path('ReporteOcurrencia/', views.ReporteOcurrencia.as_view(), name='ReporteOcurrencia'),
    path('ReporteNube/', views.ReporteNube.as_view(), name='ReporteNube'),
    path('PericiaConsultar/<int:pk>/<int:Proyectoid>/', views.PericiaConsultar.as_view(), name='PericiaConsultar'),
    path('ProyectoConsultar/<int:pk>/', views.ProyectoConsultar.as_view(), name='ProyectoConsultar'),
    path('ImagenConsultar/<int:pk>/<int:modoReport>/', views.ImagenConsultar.as_view(), name='ImagenConsultar'),
    path('BasicUpload/<int:pericia>/', views.BasicUploadView.as_view(), name='BasicUpload'),
    path('export/xls/', views.export_imagenes_xls, name='export_imagenes_xls'),
    path('export/pdf/', views.write_pdf_view, name='write_pdf_view'),
    path('ajax/load-pericias/', views.load_pericias, name='ajax_load_pericias'),
    # path('export/html/', views.download, name='download'),
]
