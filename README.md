# MuveBox 📦

Aplicación web y **API RESTful** de gestión y rastreo de paquetería, hecha con **Django** y **Django REST Framework**. Proyecto académico para el módulo *Desarrollo de Aplicaciones del Lado del Servidor*.

> Nota de nombre: este proyecto es independiente de cualquier otro proyecto llamado "Muve"; se llama **MuveBox** justamente para no mezclarlo con nada más.

## ¿Qué hace?

- Cualquier visitante puede **rastrear un paquete** por su código de seguimiento (sin iniciar sesión), como en una empresa de courier real.
- El personal (usuario con sesión iniciada) puede gestionar el **CRUD completo** de Clientes y Paquetes (crear, ver, editar, eliminar).
- Panel de **administración de Django** personalizado para gestionar todo desde `/admin/`.
- Datos de prueba generados automáticamente con la librería **Faker**.
- **API RESTful** en `/api/v1/` con respuestas JSON, autenticación **JWT** y CRUD de Clientes y Paquetes (Unidad 3).

## Stack técnico

- Python 3 + Django 6.1
- Base de datos SQLite (simple, sin servidor externo que instalar)
- Bootstrap 5 (vía CDN) para los estilos
- `python-dotenv` para variables de entorno
- `Faker` para datos de prueba
- `djangorestframework` (API RESTful) y `djangorestframework-simplejwt` (autenticación JWT)

## Estructura del proyecto

```
MuveBox/
├── config/             # Configuración del proyecto (settings, urls raíz)
├── paqueteria/          # App principal
│   ├── models.py        # Modelos: Cliente, Paquete
│   ├── views.py          # Vistas (funciones) con el CRUD
│   ├── forms.py           # Formularios (ModelForm)
│   ├── admin.py            # Personalización del admin
│   ├── urls.py              # Rutas de la app
│   ├── templates/paqueteria/ # Plantillas HTML de la app
│   ├── api/                 # API RESTful (Unidad 3)
│   │   ├── serializers.py   #   Modelo <-> JSON y validaciones
│   │   ├── views.py         #   ViewSets y vistas de autenticación
│   │   ├── urls.py          #   Rutas /api/v1/...
│   │   ├── permissions.py   #   Quién puede eliminar
│   │   ├── throttles.py     #   Límite de peticiones (login, rastreo)
│   │   ├── pagination.py    #   Formato de los listados
│   │   └── exceptions.py    #   Formato único de errores JSON
│   ├── tests.py             # Pruebas de la web (Unidades 1 y 2)
│   ├── tests_api.py         # Pruebas de la API (Unidad 3)
│   └── management/commands/seed_data.py  # Comando para generar datos de prueba
├── templates/            # Plantilla base + login
├── docs/
│   ├── api.http               # Peticiones listas para probar desde VS Code
│   └── PRUEBAS_ENDPOINTS.md   # Evidencia: respuesta real de cada endpoint
├── scripts/probar_api.py  # Prueba todos los endpoints y regenera la evidencia
├── requirements.txt
├── .env.example           # Plantilla de variables de entorno
└── USO_DE_IA.md            # Evidencia de uso de IA en el desarrollo
```

## Cómo correrlo en local

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Copiar variables de entorno
copy .env.example .env         # Windows
# cp .env.example .env         # Mac/Linux
# ...y reemplazar SECRET_KEY en .env por una clave propia, generada con:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. Aplicar migraciones
python manage.py migrate

# 5. Generar datos de prueba + usuario admin
python manage.py seed_data

# 6. Correr el servidor
python manage.py runserver
```

Luego abre `http://127.0.0.1:8000/` (web) o `http://127.0.0.1:8000/api/v1/` (API).

**Usuario de prueba creado por `seed_data`:** `admin` / `admin1234` (solo para desarrollo/evaluación local, no usar en producción). Se puede cambiar con `SEED_ADMIN_USER` y `SEED_ADMIN_PASSWORD` en `.env` antes de correr el comando.

## Correr los tests

```bash
python manage.py test                        # 39 pruebas: 7 de la web + 32 de la API
python manage.py test paqueteria.tests_api   # solo la API
```

## API RESTful (Unidad 3)

Base: `http://127.0.0.1:8000/api/v1/` · Formato: JSON · Autenticación: JWT.

### Endpoints

| Método | Ruta | Qué hace | Acceso | Éxito |
|---|---|---|---|---|
| GET | `/api/v1/` | Índice de la API | Público | 200 |
| POST | `/api/v1/auth/token/` | Login: entrega `access` y `refresh` | Público (5/min) | 200 |
| POST | `/api/v1/auth/token/refresh/` | Renueva el `access` y rota el `refresh` | Público (5/min) | 200 |
| POST | `/api/v1/auth/logout/` | Invalida el `refresh` (lista negra) | Token | 204 |
| GET | `/api/v1/auth/me/` | Datos del usuario autenticado | Token | 200 |
| GET | `/api/v1/clientes/` | Lista clientes (`?search=`, `?ordering=`, `?page=`) | Token | 200 |
| POST | `/api/v1/clientes/` | Crea un cliente | Token | 201 |
| GET | `/api/v1/clientes/{id}/` | Detalle de un cliente | Token | 200 |
| PUT | `/api/v1/clientes/{id}/` | Reemplaza un cliente | Token | 200 |
| PATCH | `/api/v1/clientes/{id}/` | Modifica campos de un cliente | Token | 200 |
| DELETE | `/api/v1/clientes/{id}/` | Elimina un cliente | Token **staff** | 204 |
| GET | `/api/v1/clientes/{id}/paquetes/` | Paquetes enviados o recibidos por el cliente | Token | 200 |
| GET | `/api/v1/paquetes/` | Lista paquetes (`?estado=`, `?search=`, `?ordering=`) | Token | 200 |
| POST | `/api/v1/paquetes/` | Crea un paquete (el código lo genera el servidor) | Token | 201 |
| GET | `/api/v1/paquetes/{id}/` | Detalle de un paquete | Token | 200 |
| PUT | `/api/v1/paquetes/{id}/` | Reemplaza un paquete | Token | 200 |
| PATCH | `/api/v1/paquetes/{id}/` | Modifica campos (ej. el `estado`) | Token | 200 |
| DELETE | `/api/v1/paquetes/{id}/` | Elimina un paquete | Token **staff** | 204 |
| GET | `/api/v1/paquetes/resumen/` | Cantidad de paquetes por estado | Token | 200 |
| GET | `/api/v1/rastreo/{codigo}/` | Estado de un paquete por código | Público (30/min) | 200 |

Códigos de error: `400` datos inválidos · `401` sin token o token inválido · `403` sin permiso · `404` no existe · `405` método no permitido · `429` demasiadas peticiones.

### Cómo autenticarse

```bash
# 1. Pedir los tokens (cmd de Windows)
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ -H "Content-Type: application/json" -d "{\"username\": \"admin\", \"password\": \"admin1234\"}"
# -> {"refresh": "eyJ...", "access": "eyJ..."}

# 2. Usar el access en cada petición
curl http://127.0.0.1:8000/api/v1/paquetes/ -H "Authorization: Bearer <access>"
```

El `access` dura 15 minutos. Cuando expira se pide otro en `/auth/token/refresh/` enviando el `refresh` (dura 1 día y cambia en cada renovación).

### Formato de las respuestas

Listado (siempre paginado):

```json
{
  "total": 20, "paginas": 2, "pagina_actual": 1,
  "siguiente": "http://127.0.0.1:8000/api/v1/paquetes/?page=2", "anterior": null,
  "resultados": [ { "id": 1, "codigo_seguimiento": "MUV-A1B2C3", "estado": "PENDIENTE", "...": "..." } ]
}
```

Error (misma estructura para todos los errores):

```json
{
  "error": {
    "codigo": "solicitud_invalida",
    "mensaje": "Los datos enviados no son válidos.",
    "detalles": { "peso_kg": ["El peso debe ser mayor que 0 kg."] }
  }
}
```

### Cómo probar los endpoints

- **Automático:** `python manage.py test` (no necesita el servidor corriendo).
- **Contra el servidor real:** con `runserver` corriendo, en otra terminal `python scripts/probar_api.py`. Recorre 34 peticiones y guarda cada respuesta en [docs/PRUEBAS_ENDPOINTS.md](docs/PRUEBAS_ENDPOINTS.md).
- **A mano:** abrir [docs/api.http](docs/api.http) en VS Code con la extensión *REST Client*, o copiar las mismas peticiones en Postman/Thunder Client.
- **Desde el navegador:** con `DEBUG=True`, iniciar sesión en `/login/` y entrar a `/api/v1/` (API navegable de DRF).

### Medidas de seguridad aplicadas

| Medida | Dónde | Por qué |
|---|---|---|
| Todo endpoint exige autenticación por defecto | `REST_FRAMEWORK.DEFAULT_PERMISSION_CLASSES` | Un endpoint nuevo queda protegido aunque se olvide declararlo; lo público se marca a propósito |
| JWT con `access` de 15 min | `SIMPLE_JWT` en `settings.py` | Un token robado sirve por poco tiempo |
| Rotación y lista negra del `refresh` | `SIMPLE_JWT` + `auth/logout/` | Un `refresh` usado o de una sesión cerrada no se puede reutilizar |
| Límite de intentos de login (5/min por IP) | `api/throttles.py` | Frena ataques de fuerza bruta de contraseñas |
| Límite en el rastreo público (30/min por IP) | `api/throttles.py` | Dificulta adivinar códigos de seguimiento en masa |
| Rastreo público con datos mínimos | `RastreoSerializer` | Sin token no se exponen nombres, correos, direcciones ni notas |
| Solo el personal elimina | `api/permissions.py` | Mínimo privilegio: borrar no se puede deshacer |
| Campos de solo lectura y validaciones | `api/serializers.py` | El cliente no puede fijar `id` ni `codigo_seguimiento`, ni enviar datos incoherentes |
| Código de seguimiento con `secrets` | `models.py` | `random` es predecible; el código da acceso sin sesión |
| `SECRET_KEY` y `DEBUG` en `.env` | `settings.py`, `.gitignore` | La clave firma los JWT; sin ella y con `DEBUG=False` el proyecto no arranca |
| API navegable y sesión solo con `DEBUG=True` | `settings.py` | En producción la API solo responde JSON y solo acepta JWT |
| HTTPS, HSTS y cookies seguras con `DEBUG=False` | `settings.py` | Los tokens viajan en cabeceras: sin HTTPS se pueden interceptar |
| Contraseñas con hash y validadores de Django | `AUTH_PASSWORD_VALIDATORS` | Nunca se guardan ni se devuelven en texto plano |

El análisis de por qué se eligió cada una (y qué recomendaciones de la IA se descartaron) está en `USO_DE_IA.md`.

## Mapeo con la rúbrica del profesor

**Evaluación 3 — API RESTful (Unidad 3)**

| Indicador | Dónde se evidencia |
|---|---|
| 1. Configura DRF según documentación oficial | `config/settings.py` (`INSTALLED_APPS`, `REST_FRAMEWORK`, `SIMPLE_JWT`), `requirements.txt`, paquete `paqueteria/api/` separado por responsabilidad |
| 2. Implementa autenticación | JWT: `auth/token/`, `auth/token/refresh/`, `auth/logout/`, `auth/me/` en `api/views.py` y `api/urls.py`; pruebas en `AutenticacionTests` |
| 3. Recomendaciones de seguridad en la autenticación | Tabla "Medidas de seguridad aplicadas" de este README + justificación en `USO_DE_IA.md` |
| 4. Respuestas en formato JSON | `api/serializers.py`, `api/pagination.py`, `api/exceptions.py`; ejemplos reales en `docs/PRUEBAS_ENDPOINTS.md` |
| 5. Endpoints según requerimientos | Tabla "Endpoints" de este README; `api/urls.py` (router) y `api/views.py` (ViewSets) |
| 6. Características RESTful | Recursos en plural, métodos GET/POST/PUT/PATCH/DELETE, códigos 200/201/204/400/401/403/404/405/429, versión en la URL (`/api/v1/`), sin estado (JWT) |
| 7. Uso de IA como apoyo | `USO_DE_IA.md`, sección "Unidad 3" |

Productos esperados: proyecto funcional ✔ · DRF configurado ✔ · recursos expuestos (`Cliente`, `Paquete`) ✔ · endpoints ✔ · JSON ✔ · operaciones HTTP ✔ · autenticación ✔ · seguridad ✔ · pruebas (`tests_api.py`, `docs/PRUEBAS_ENDPOINTS.md`) ✔ · evidencia de IA (`USO_DE_IA.md`) ✔ · README ✔

**Evaluación 1 — Tecnologías del lado del servidor y Django**

| Indicador | Dónde se evidencia |
|---|---|
| 1. Variables y operaciones | `paqueteria/models.py`, `views.py` (lógica de filtros, agregaciones) |
| 2. Instrucciones, estructuras y operadores | `views.py` (condicionales, querysets, decoradores) |
| 3. Paquetes externos | `Faker` (datos de prueba), `python-dotenv` (variables de entorno) — ver `requirements.txt` |
| 4. Aplicación Django funcional | Todo el proyecto: modelos + vistas + templates + admin |
| 5. Patrón MVC (MVT en Django) | Modelos (`models.py`) / Vistas (`views.py`) / Templates (`templates/`) claramente separados |
| 6. Configuración del entorno Django | `config/settings.py`, `.env` / `.env.example` |
| 7. Django Models | `Cliente` y `Paquete` en `models.py`, con relaciones (`ForeignKey`) |
| 8. Vistas y templates | CRUD completo en `views.py` + `templates/paqueteria/*.html` |
| 9. Tecnologías del lado del servidor | Django (backend), SQLite (persistencia), sesiones HTTP |
| 10. Uso de IA | Ver `USO_DE_IA.md` |
| 11. Datos de prueba con IA | `python manage.py seed_data` (usa Faker) — ver `USO_DE_IA.md` |
| 12. Protocolos, hosting y dominios | Ver sección "Despliegue" más abajo |

**Evaluación 2 — Django Admin y CRUD**

| Indicador | Dónde se evidencia |
|---|---|
| Configuración de base de datos | `config/settings.py` → `DATABASES` (SQLite, simple de revisar) |
| Uso de Django Admin | `paqueteria/admin.py`: `list_display`, `search_fields`, `list_filter`, acciones masivas personalizadas |
| Operaciones CRUD | Funciones `paquete_create/update/delete/detail/list` y `cliente_*` en `views.py` |
| Backend + seguridad | `@login_required` en vistas de gestión, CSRF en todos los formularios, contraseñas con hash (Django auth) |
| Sesiones y autenticación | `django.contrib.auth` (login/logout), `LOGIN_URL`, rutas protegidas |
| Uso de IA | Ver `USO_DE_IA.md` |

## Despliegue (protocolos, hosting y dominios)

Este proyecto corre en local sobre HTTP (`http://127.0.0.1:8000`). Para publicarlo en internet con un dominio propio, los pasos conceptuales serían:

1. **Hosting**: subir el proyecto a un servicio como Railway, Render o PythonAnywhere (todos tienen plan gratuito para proyectos chicos).
2. **Base de datos**: en producción normalmente se cambia SQLite por PostgreSQL (el hosting lo provee).
3. **Variables de entorno**: configurar `SECRET_KEY`, `DEBUG=False` y `ALLOWED_HOSTS` con el dominio real en el panel del hosting (nunca subir `.env` a GitHub).
4. **Dominio**: se compra un dominio (ej. en NIC Chile o Namecheap) y se apunta con un registro DNS tipo `A` o `CNAME` hacia la IP/URL que entrega el hosting.
5. **HTTPS**: la mayoría de estos hosting dan certificado SSL automático, para que el sitio use `https://` en vez de `http://`.

## Autor

Proyecto desarrollado por Leonardo con apoyo de IA (Claude) para la generación inicial del código — ver `USO_DE_IA.md` para el detalle de qué se hizo con IA y qué se personalizó a mano.
