from django.urls import path

from . import views

app_name = "paqueteria"

urlpatterns = [
    path("", views.home, name="home"),
    path("rastrear/", views.rastrear_paquete, name="rastrear"),
    path("paquetes/", views.paquete_list, name="paquete_list"),
    path("paquetes/nuevo/", views.paquete_create, name="paquete_create"),
    path("paquetes/<int:pk>/", views.paquete_detail, name="paquete_detail"),
    path("paquetes/<int:pk>/editar/", views.paquete_update, name="paquete_update"),
    path("paquetes/<int:pk>/eliminar/", views.paquete_delete, name="paquete_delete"),
    path("clientes/", views.cliente_list, name="cliente_list"),
    path("clientes/nuevo/", views.cliente_create, name="cliente_create"),
    path("clientes/<int:pk>/", views.cliente_detail, name="cliente_detail"),
    path("clientes/<int:pk>/editar/", views.cliente_update, name="cliente_update"),
    path("clientes/<int:pk>/eliminar/", views.cliente_delete, name="cliente_delete"),
]
