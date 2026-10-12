"""Pruebas de la API RESTful (Unidad 3). Ejecutar con: python manage.py test"""
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cliente, Paquete

CLAVE = "Clave-Segura-2026"


class BaseAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.operador = User.objects.create_user("operador", password=CLAVE)
        cls.staff = User.objects.create_user("jefa", password=CLAVE, is_staff=True)
        cls.ana = Cliente.objects.create(nombre="Ana Soto", email="ana@example.com")
        cls.luis = Cliente.objects.create(nombre="Luis Rojas", email="luis@example.com")
        cls.paquete = Paquete.objects.create(
            remitente=cls.ana,
            destinatario=cls.luis,
            descripcion="Caja de libros",
            peso_kg="2.50",
            direccion_entrega="Av. Siempre Viva 742",
            notas="Nota interna",
        )

    def setUp(self):
        # Los contadores de throttling viven en caché: se limpian entre pruebas.
        cache.clear()

    def datos_paquete(self, **cambios):
        datos = {
            "remitente": self.ana.pk,
            "destinatario": self.luis.pk,
            "descripcion": "Notebook",
            "peso_kg": "1.80",
            "direccion_entrega": "Los Aromos 123",
        }
        datos.update(cambios)
        return datos


class AutenticacionTests(BaseAPITestCase):
    def login(self, password=CLAVE):
        return self.client.post(
            reverse("api:token_obtener"), {"username": "operador", "password": password}
        )

    def test_login_correcto_entrega_tokens(self):
        response = self.login()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_con_clave_incorrecta_responde_401(self):
        response = self.login("clave-mala")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error"]["codigo"], "no_autenticado")

    def test_endpoint_protegido_sin_token_responde_401(self):
        response = self.client.get(reverse("api:paquete-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_invalido_responde_401(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer token.falso.123")
        response = self.client.get(reverse("api:paquete-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_token_permite_entrar(self):
        access = self.login().data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.get(reverse("api:usuario_actual"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "operador")
        self.assertNotIn("password", response.data)

    def test_refresh_rota_el_token_y_el_anterior_queda_invalido(self):
        refresh = self.login().data["refresh"]
        url = reverse("api:token_renovar")
        primera = self.client.post(url, {"refresh": refresh})
        self.assertEqual(primera.status_code, status.HTTP_200_OK)
        self.assertNotEqual(primera.data["refresh"], refresh)
        segunda = self.client.post(url, {"refresh": refresh})
        self.assertEqual(segunda.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_deja_el_refresh_en_lista_negra(self):
        tokens = self.login().data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = self.client.post(reverse("api:logout"), {"refresh": tokens["refresh"]})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client.credentials()
        response = self.client.post(reverse("api:token_renovar"), {"refresh": tokens["refresh"]})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_se_bloquea_tras_demasiados_intentos(self):
        for _ in range(5):
            self.assertEqual(self.login("clave-mala").status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.login("clave-mala")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.data["error"]["codigo"], "demasiadas_peticiones")


class ClienteAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(self.operador)

    def test_listar_devuelve_json_paginado(self):
        response = self.client.get(reverse("api:cliente-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(
            set(response.data), {"total", "paginas", "pagina_actual", "siguiente", "anterior", "resultados"}
        )
        self.assertEqual(response.data["total"], 2)

    def test_crear_responde_201(self):
        response = self.client.post(
            reverse("api:cliente-list"), {"nombre": "Marta Díaz", "email": "marta@example.com"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total_enviados"], 0)
        self.assertTrue(Cliente.objects.filter(email="marta@example.com").exists())

    def test_crear_con_email_repetido_responde_400(self):
        response = self.client.post(
            reverse("api:cliente-list"), {"nombre": "Otra Ana", "email": "ana@example.com"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["error"]["detalles"])

    def test_detalle_incluye_contadores(self):
        response = self.client.get(reverse("api:cliente-detail", args=[self.ana.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_enviados"], 1)
        self.assertEqual(response.data["total_recibidos"], 0)

    def test_detalle_inexistente_responde_404(self):
        response = self.client.get(reverse("api:cliente-detail", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"]["codigo"], "no_encontrado")

    def test_put_reemplaza_y_patch_modifica_parcialmente(self):
        url = reverse("api:cliente-detail", args=[self.ana.pk])
        response = self.client.put(url, {"nombre": "Ana S.", "email": "ana@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(url, {"telefono": "+56 9 1111 2222"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ana.refresh_from_db()
        self.assertEqual((self.ana.nombre, self.ana.telefono), ("Ana S.", "+56 9 1111 2222"))

    def test_buscar_por_nombre(self):
        response = self.client.get(reverse("api:cliente-list"), {"search": "luis"})
        self.assertEqual([c["nombre"] for c in response.data["resultados"]], ["Luis Rojas"])

    def test_paquetes_del_cliente(self):
        response = self.client.get(reverse("api:cliente-paquetes", args=[self.luis.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 1)

    def test_eliminar_sin_ser_staff_responde_403(self):
        response = self.client.delete(reverse("api:cliente-detail", args=[self.ana.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Cliente.objects.filter(pk=self.ana.pk).exists())

    def test_eliminar_como_staff_responde_204(self):
        self.client.force_authenticate(self.staff)
        response = self.client.delete(reverse("api:cliente-detail", args=[self.ana.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cliente.objects.filter(pk=self.ana.pk).exists())


class PaqueteAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(self.operador)

    def test_crear_genera_codigo_y_estado_por_defecto(self):
        response = self.client.post(reverse("api:paquete-list"), self.datos_paquete())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["codigo_seguimiento"].startswith("MUV-"))
        self.assertEqual(response.data["estado"], "PENDIENTE")
        self.assertEqual(response.data["remitente_detalle"]["nombre"], "Ana Soto")

    def test_el_codigo_de_seguimiento_no_se_puede_fijar_ni_cambiar(self):
        response = self.client.post(
            reverse("api:paquete-list"), self.datos_paquete(codigo_seguimiento="MUV-HACKED")
        )
        self.assertNotEqual(response.data["codigo_seguimiento"], "MUV-HACKED")
        original = self.paquete.codigo_seguimiento
        self.client.patch(
            reverse("api:paquete-detail", args=[self.paquete.pk]), {"codigo_seguimiento": "MUV-HACKED"}
        )
        self.paquete.refresh_from_db()
        self.assertEqual(self.paquete.codigo_seguimiento, original)

    def test_validaciones_responden_400(self):
        casos = {
            "peso_kg": self.datos_paquete(peso_kg="-1"),
            "destinatario": self.datos_paquete(destinatario=self.ana.pk),
            "estado": self.datos_paquete(estado="PERDIDO"),
            "descripcion": self.datos_paquete(descripcion=""),
        }
        for campo, datos in casos.items():
            with self.subTest(campo=campo):
                response = self.client.post(reverse("api:paquete-list"), datos)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data["error"]["codigo"], "solicitud_invalida")
                self.assertIn(campo, response.data["error"]["detalles"])

    def test_patch_no_permite_dejar_remitente_igual_a_destinatario(self):
        response = self.client.patch(
            reverse("api:paquete-detail", args=[self.paquete.pk]), {"destinatario": self.ana.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_cambia_el_estado(self):
        response = self.client.patch(
            reverse("api:paquete-detail", args=[self.paquete.pk]), {"estado": "EN_TRANSITO"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["estado_descripcion"], "En tránsito")

    def test_filtrar_por_estado(self):
        url = reverse("api:paquete-list")
        self.assertEqual(self.client.get(url, {"estado": "PENDIENTE"}).data["total"], 1)
        self.assertEqual(self.client.get(url, {"estado": "ENTREGADO"}).data["total"], 0)
        self.assertEqual(self.client.get(url, {"estado": "XX"}).status_code, status.HTTP_400_BAD_REQUEST)

    def test_resumen_por_estado(self):
        response = self.client.get(reverse("api:paquete-resumen"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 1)
        self.assertEqual(response.data["por_estado"]["PENDIENTE"], 1)
        self.assertEqual(response.data["por_estado"]["ENTREGADO"], 0)

    def test_metodo_no_permitido_responde_405(self):
        response = self.client.post(reverse("api:paquete-detail", args=[self.paquete.pk]), {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_eliminar_solo_staff(self):
        url = reverse("api:paquete-detail", args=[self.paquete.pk])
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_204_NO_CONTENT)


class EndpointsPublicosTests(BaseAPITestCase):
    def test_raiz_de_la_api_es_publica(self):
        response = self.client.get(reverse("api:raiz"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("recursos", response.data)

    def test_rastreo_sin_token_muestra_solo_datos_minimos(self):
        codigo = self.paquete.codigo_seguimiento
        response = self.client.get(reverse("api:rastreo", args=[codigo.lower()]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {"codigo_seguimiento", "estado", "estado_descripcion", "fecha_creacion", "fecha_actualizacion"},
        )

    def test_rastreo_de_codigo_inexistente_responde_404(self):
        response = self.client.get(reverse("api:rastreo", args=["MUV-000000"]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rastreo_es_solo_lectura(self):
        response = self.client.delete(reverse("api:rastreo", args=[self.paquete.codigo_seguimiento]))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_ruta_inexistente_de_la_api_responde_404_en_json(self):
        response = self.client.get("/api/v1/no-existe/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json()["error"]["codigo"], "no_encontrado")
