from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Cliente, Paquete


class ClienteModelTests(TestCase):
    def test_str_devuelve_nombre(self):
        cliente = Cliente.objects.create(nombre="Ana Soto", email="ana@example.com")
        self.assertEqual(str(cliente), "Ana Soto")


class PaqueteModelTests(TestCase):
    def setUp(self):
        self.remitente = Cliente.objects.create(nombre="Remitente", email="rem@example.com")
        self.destinatario = Cliente.objects.create(nombre="Destinatario", email="dest@example.com")

    def test_codigo_seguimiento_se_genera_automaticamente(self):
        paquete = Paquete.objects.create(
            remitente=self.remitente,
            destinatario=self.destinatario,
            descripcion="Caja de prueba",
            peso_kg=1.5,
            direccion_entrega="Calle Falsa 123",
        )
        self.assertTrue(paquete.codigo_seguimiento.startswith("MUV-"))

    def test_estado_por_defecto_pendiente(self):
        paquete = Paquete.objects.create(
            remitente=self.remitente,
            destinatario=self.destinatario,
            descripcion="Caja de prueba",
            peso_kg=1.5,
            direccion_entrega="Calle Falsa 123",
        )
        self.assertEqual(paquete.estado, Paquete.Estado.PENDIENTE)


class VistasPublicasTests(TestCase):
    def test_home_responde_200(self):
        response = self.client.get(reverse("paqueteria:home"))
        self.assertEqual(response.status_code, 200)

    def test_rastrear_responde_200(self):
        response = self.client.get(reverse("paqueteria:rastrear"))
        self.assertEqual(response.status_code, 200)


class VistasProtegidasTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("tester", password="clave12345")

    def test_paquete_list_redirige_si_no_hay_sesion(self):
        response = self.client.get(reverse("paqueteria:paquete_list"))
        self.assertEqual(response.status_code, 302)

    def test_paquete_list_accesible_con_sesion(self):
        self.client.login(username="tester", password="clave12345")
        response = self.client.get(reverse("paqueteria:paquete_list"))
        self.assertEqual(response.status_code, 200)
