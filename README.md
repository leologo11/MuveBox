# MuveBox 📦

Aplicación web simple de gestión y rastreo de paquetería, hecha con **Django**. Proyecto académico para el módulo *Desarrollo de Aplicaciones del Lado del Servidor*.

> Nota de nombre: este proyecto es independiente de cualquier otro proyecto llamado "Muve"; se llama **MuveBox** justamente para no mezclarlo con nada más.

## ¿Qué hace?

- Cualquier visitante puede **rastrear un paquete** por su código de seguimiento (sin iniciar sesión), como en una empresa de courier real.
- El personal (usuario con sesión iniciada) puede gestionar el **CRUD completo** de Clientes y Paquetes (crear, ver, editar, eliminar).
- Panel de **administración de Django** personalizado para gestionar todo desde `/admin/`.
- Datos de prueba generados automáticamente con la librería **Faker**.

## Stack técnico

- Python 3 + Django 6.1
- Base de datos SQLite (simple, sin servidor externo que instalar)
- Bootstrap 5 (vía CDN) para los estilos
- `python-dotenv` para variables de entorno
- `Faker` para datos de prueba

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
│   └── management/commands/seed_data.py  # Comando para generar datos de prueba
├── templates/            # Plantilla base + login
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

# 4. Aplicar migraciones
python manage.py migrate

# 5. Generar datos de prueba + usuario admin
python manage.py seed_data

# 6. Correr el servidor
python manage.py runserver
```

Luego abre `http://127.0.0.1:8000/`.

**Usuario de prueba creado por `seed_data`:** `admin` / `admin1234` (solo para desarrollo/evaluación local, no usar en producción).

## Correr los tests

```bash
python manage.py test
```

## Mapeo con la rúbrica del profesor

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
