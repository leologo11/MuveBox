from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

app_name = "api"

# El router genera las rutas REST de cada recurso:
#   /clientes/        GET (listar)  POST (crear)
#   /clientes/{id}/   GET (detalle) PUT/PATCH (modificar) DELETE (eliminar)
router = SimpleRouter()
router.register("clientes", views.ClienteViewSet, basename="cliente")
router.register("paquetes", views.PaqueteViewSet, basename="paquete")

urlpatterns = [
    path("", views.RaizAPIView.as_view(), name="raiz"),
    path("auth/token/", views.LoginView.as_view(), name="token_obtener"),
    path("auth/token/refresh/", views.RenovarTokenView.as_view(), name="token_renovar"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("auth/me/", views.UsuarioActualView.as_view(), name="usuario_actual"),
    path("rastreo/<str:codigo>/", views.RastreoView.as_view(), name="rastreo"),
    path("", include(router.urls)),
]
