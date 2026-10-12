from django.db.models import Count, Q
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from ..models import Cliente, Paquete
from .permissions import SoloStaffElimina
from .serializers import (
    ClienteSerializer,
    LogoutSerializer,
    PaqueteSerializer,
    RastreoSerializer,
    UsuarioSerializer,
)
from .throttles import LoginThrottle, RastreoThrottle


class RaizAPIView(APIView):
    """Punto de entrada de la API: lista los recursos disponibles."""

    permission_classes = [AllowAny]

    def get(self, request):
        def url(nombre):
            return reverse(nombre, request=request)

        return Response(
            {
                "nombre": "MuveBox API",
                "version": "v1",
                "autenticacion": {
                    "tipo": "JWT (cabecera Authorization: Bearer <access>)",
                    "obtener_token": url("api:token_obtener"),
                    "renovar_token": url("api:token_renovar"),
                    "cerrar_sesion": url("api:logout"),
                    "usuario_actual": url("api:usuario_actual"),
                },
                "recursos": {
                    "clientes": url("api:cliente-list"),
                    "paquetes": url("api:paquete-list"),
                    "resumen_paquetes": url("api:paquete-resumen"),
                    "rastreo_publico": reverse("api:rastreo", args=["MUV-XXXXXX"], request=request),
                },
            }
        )


class RutaNoEncontradaView(APIView):
    """Cualquier ruta inexistente bajo /api/ responde 404 en JSON (no en HTML)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def initial(self, request, *args, **kwargs):
        raise NotFound("El recurso solicitado no existe. Revisa la ruta (todas terminan en '/').")


# ---------- Autenticación ----------

class LoginView(TokenObtainPairView):
    """POST usuario y contraseña -> devuelve tokens `access` y `refresh`."""

    throttle_classes = [LoginThrottle]


class RenovarTokenView(TokenRefreshView):
    """POST `refresh` -> devuelve un `access` nuevo (y rota el `refresh`)."""

    throttle_classes = [LoginThrottle]


class LogoutView(APIView):
    """POST `refresh` -> lo deja en lista negra, así no se puede volver a usar."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except TokenError:
            raise ValidationError({"refresh": "El token no es válido o ya expiró."})
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsuarioActualView(generics.RetrieveAPIView):
    """GET -> datos del usuario dueño del token."""

    serializer_class = UsuarioSerializer

    def get_object(self):
        return self.request.user


# ---------- Recursos ----------

class ClienteViewSet(viewsets.ModelViewSet):
    """CRUD de clientes: list, create, retrieve, update, partial_update, destroy."""

    serializer_class = ClienteSerializer
    permission_classes = [SoloStaffElimina]
    search_fields = ["nombre", "email", "telefono"]
    ordering_fields = ["nombre", "fecha_registro"]
    ordering = ["nombre"]

    def get_queryset(self):
        return Cliente.objects.annotate(
            total_enviados=Count("paquetes_enviados", distinct=True),
            total_recibidos=Count("paquetes_recibidos", distinct=True),
        )

    def perform_create(self, serializer):
        # Se vuelve a leer para devolver los contadores (total_enviados...) en el 201.
        serializer.instance = self.get_queryset().get(pk=serializer.save().pk)

    def perform_update(self, serializer):
        serializer.instance = self.get_queryset().get(pk=serializer.save().pk)

    @action(detail=True, methods=["get"])
    def paquetes(self, request, pk=None):
        """GET /clientes/{id}/paquetes/ -> paquetes enviados o recibidos por el cliente."""
        cliente = self.get_object()
        paquetes = Paquete.objects.select_related("remitente", "destinatario").filter(
            Q(remitente=cliente) | Q(destinatario=cliente)
        )
        pagina = self.paginate_queryset(paquetes)
        serializer = PaqueteSerializer(pagina, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class PaqueteViewSet(viewsets.ModelViewSet):
    """CRUD de paquetes. Filtros: ?estado=EN_TRANSITO, ?search=texto, ?ordering=-peso_kg"""

    serializer_class = PaqueteSerializer
    permission_classes = [SoloStaffElimina]
    search_fields = ["codigo_seguimiento", "descripcion", "remitente__nombre", "destinatario__nombre"]
    ordering_fields = ["fecha_creacion", "fecha_actualizacion", "peso_kg", "estado"]
    ordering = ["-fecha_creacion"]

    def get_queryset(self):
        paquetes = Paquete.objects.select_related("remitente", "destinatario")
        estado = self.request.query_params.get("estado")
        if estado:
            if estado not in Paquete.Estado.values:
                raise ValidationError(
                    {"estado": f"Valor no válido. Opciones: {', '.join(Paquete.Estado.values)}."}
                )
            paquetes = paquetes.filter(estado=estado)
        return paquetes

    @action(detail=False, methods=["get"])
    def resumen(self, request):
        """GET /paquetes/resumen/ -> cantidad de paquetes por estado."""
        conteos = dict(
            Paquete.objects.values_list("estado").annotate(cantidad=Count("id"))
        )
        por_estado = {estado: conteos.get(estado, 0) for estado in Paquete.Estado.values}
        return Response({"total": sum(por_estado.values()), "por_estado": por_estado})


class RastreoView(generics.RetrieveAPIView):
    """
    GET /rastreo/{codigo}/ -> estado de un paquete. Público (sin token),
    solo lectura, con datos mínimos y límite de peticiones por IP.
    """

    serializer_class = RastreoSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [RastreoThrottle]
    queryset = Paquete.objects.all()
    lookup_field = "codigo_seguimiento"
    lookup_url_kwarg = "codigo"

    def get_object(self):
        self.kwargs["codigo"] = self.kwargs["codigo"].strip().upper()
        return super().get_object()
