import secrets
import string

from django.db import models
from django.urls import reverse


def generar_codigo_seguimiento():
    """Genera un código único tipo MUV-A1B2C3 para rastrear el paquete."""
    # secrets (y no random): el código permite consultar el paquete sin iniciar
    # sesión, así que no debe ser predecible.
    alfabeto = string.ascii_uppercase + string.digits
    sufijo = "".join(secrets.choice(alfabeto) for _ in range(6))
    return f"MUV-{sufijo}"


class Cliente(models.Model):
    nombre = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse("paqueteria:cliente_detail", args=[self.pk])


class Paquete(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente de retiro"
        EN_TRANSITO = "EN_TRANSITO", "En tránsito"
        ENTREGADO = "ENTREGADO", "Entregado"
        CANCELADO = "CANCELADO", "Cancelado"

    codigo_seguimiento = models.CharField(
        max_length=15, unique=True, default=generar_codigo_seguimiento, editable=False
    )
    remitente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="paquetes_enviados"
    )
    destinatario = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="paquetes_recibidos"
    )
    descripcion = models.CharField(max_length=200)
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2)
    direccion_entrega = models.CharField(max_length=200)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    notas = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.codigo_seguimiento} ({self.get_estado_display()})"

    def get_absolute_url(self):
        return reverse("paqueteria:paquete_detail", args=[self.pk])
