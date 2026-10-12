"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path

from paqueteria.api.views import RutaNoEncontradaView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # API RESTful versionada (Unidad 3)
    path("api/v1/", include("paqueteria.api.urls")),
    re_path(r"^api/", RutaNoEncontradaView.as_view()),
    path("", include("paqueteria.urls")),
]
