from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..models import Cliente, Paquete


class ClienteSerializer(serializers.ModelSerializer):
    total_enviados = serializers.IntegerField(read_only=True)
    total_recibidos = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cliente
        fields = [
            "id",
            "nombre",
            "email",
            "telefono",
            "direccion",
            "fecha_registro",
            "total_enviados",
            "total_recibidos",
        ]
        read_only_fields = ["id", "fecha_registro"]


class ClienteResumenSerializer(serializers.ModelSerializer):
    """Versión corta del cliente, para anidarla dentro de un paquete."""

    class Meta:
        model = Cliente
        fields = ["id", "nombre", "email"]


class PaqueteSerializer(serializers.ModelSerializer):
    # Al escribir se envía el id del cliente (remitente / destinatario);
    # al leer se entrega además el detalle resumido, para ahorrar peticiones.
    remitente_detalle = ClienteResumenSerializer(source="remitente", read_only=True)
    destinatario_detalle = ClienteResumenSerializer(source="destinatario", read_only=True)
    estado_descripcion = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Paquete
        fields = [
            "id",
            "codigo_seguimiento",
            "remitente",
            "remitente_detalle",
            "destinatario",
            "destinatario_detalle",
            "descripcion",
            "peso_kg",
            "direccion_entrega",
            "estado",
            "estado_descripcion",
            "notas",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        # El código lo genera el servidor: el cliente de la API no puede fijarlo.
        read_only_fields = ["id", "codigo_seguimiento", "fecha_creacion", "fecha_actualizacion"]

    def validate_peso_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("El peso debe ser mayor que 0 kg.")
        return value

    def validate(self, attrs):
        # En un PATCH puede venir solo uno de los dos; el otro se toma del registro.
        remitente = attrs.get("remitente", getattr(self.instance, "remitente", None))
        destinatario = attrs.get("destinatario", getattr(self.instance, "destinatario", None))
        if remitente and destinatario and remitente == destinatario:
            raise serializers.ValidationError(
                {"destinatario": "El destinatario no puede ser el mismo cliente que el remitente."}
            )
        return attrs


class RastreoSerializer(serializers.ModelSerializer):
    """
    Datos visibles en el rastreo público (sin autenticación).

    Se exponen solo los campos necesarios para saber dónde está el paquete:
    nada de nombres, correos, direcciones ni notas internas.
    """

    estado_descripcion = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Paquete
        fields = [
            "codigo_seguimiento",
            "estado",
            "estado_descripcion",
            "fecha_creacion",
            "fecha_actualizacion",
        ]


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        # La contraseña (ni su hash) nunca sale por la API.
        fields = ["id", "username", "email", "first_name", "last_name", "is_staff"]
        read_only_fields = fields


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
