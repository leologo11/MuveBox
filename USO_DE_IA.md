# Evidencia de uso de Inteligencia Artificial

Este documento explica, de forma honesta, qué partes del proyecto **MuveBox** se generaron con apoyo de IA (Claude Code, de Anthropic) y qué se espera que el estudiante revise, entienda y personalice antes de entregar. El objetivo es cumplir con el criterio de "uso estratégico de IA" de la rúbrica: **usar la IA como apoyo, no como reemplazo del aprendizaje**.

## 1. Qué se generó con apoyo de IA

- Estructura inicial del proyecto Django (`config/`, app `paqueteria`).
- Modelos `Cliente` y `Paquete`, incluyendo la relación entre ambos.
- Vistas (funciones) para el CRUD de Paquetes y Clientes, y la vista pública de rastreo.
- Plantillas HTML con Bootstrap para que se vea ordenado sin invertir horas en CSS.
- Configuración del panel de administración (`admin.py`) con búsqueda, filtros y una acción masiva ("marcar como entregado").
- Comando `seed_data` que usa la librería **Faker** para generar clientes y paquetes de prueba realistas (nombres, direcciones, teléfonos chilenos).
- Un set de pruebas automatizadas básicas (`paqueteria/tests.py`).

## 2. Ejemplos de prompts usados

> "Necesito un proyecto Django simple llamado MuveBox sobre paquetería, con CRUD de paquetes y clientes, admin personalizado, login/sesiones y datos de prueba con Faker, que cumpla esta rúbrica: [rúbrica del profesor]."

> "Genera un comando de management que cree datos de prueba realistas con Faker en español, y un superusuario por defecto para probar el admin."

## 3. Cómo se validaron las recomendaciones de la IA (no se copió a ciegas)

- Se corrió `python manage.py check` y `migrate` para confirmar que los modelos son válidos.
- Se escribieron y ejecutaron **7 tests automatizados** (`python manage.py test`) que verifican modelos, vistas públicas y vistas protegidas por login.
- Se probó manualmente el flujo completo por HTTP: login real, listado de paquetes con datos, panel admin, y la búsqueda pública de rastreo con un código real generado por Faker.
- Se revisó que las vistas de gestión (`paquetes/`, `clientes/`) queden protegidas con `@login_required` y que los formularios tengan protección CSRF.

## 4. Qué debe personalizar el estudiante (para que el mérito también sea propio)

Estas son tareas cortas pero **hazlas tú mismo/a** antes de entregar, así puedes explicarlas si el profesor pregunta:

1. **Cambia algo del diseño**: color de la barra de navegación o del dashboard en `templates/base.html` (busca `bg-dark`, cámbialo por ejemplo a `bg-primary` o al color que prefieras).
2. **Agrega un campo propio** a `Paquete` (ej. `prioridad`, `fecha_estimada_entrega` o `es_fragil`) en `paqueteria/models.py`, corre `python manage.py makemigrations` y `migrate`, y agrégalo también al formulario en `forms.py`.
3. **Personaliza los datos de prueba**: edita la lista `DESCRIPCIONES` en `paqueteria/management/commands/seed_data.py` con ejemplos propios.
4. **Cambia las credenciales del admin de prueba** (usuario/clave en `seed_data.py`) por unas propias.
5. **Escribe con tus palabras** (en el informe o en un comentario aparte) qué hace el patrón MVT en este proyecto específico: cuál archivo es el "Modelo", cuál la "Vista" y cuál la "Plantilla", con un ejemplo real de este código.
6. Antes de subir a GitHub, **revisa el código y quita/ajusta cualquier parte que no entiendas** — es mejor achicar el proyecto que entregar algo que no puedes explicar.

## 5. Qué NO se automatizó

El profesor pidió explícitamente que las recomendaciones de IA se **evalúen y adapten**, no que se usen tal cual. Por eso este documento queda como evidencia junto con el código: el proyecto funciona (probado con tests + pruebas manuales), pero la lista de la sección 4 es la parte donde el estudiante deja su propia huella antes de entregar.

---

# Unidad 3 — API RESTful: uso de IA en el desarrollo y la seguridad

La API (`paqueteria/api/`, `/api/v1/`) se desarrolló con apoyo de **Claude Code (Anthropic)**. Esta sección registra qué se le pidió, qué recomendó, cómo se comprobó cada recomendación, cuáles se adaptaron o descartaron y qué riesgos quedan abiertos.

## U3.1 Qué se le pidió a la IA

> "Lee la escala de apreciación de la Unidad 3 (API RESTful con Django REST Framework) y agrega al proyecto MuveBox todo lo necesario para cumplirla: configuración de DRF, autenticación, respuestas JSON, endpoints RESTful, medidas de seguridad, pruebas y README."

Con ese encargo la IA generó: la configuración de DRF y JWT en `settings.py`, el paquete `paqueteria/api/` (serializers, vistas, rutas, permisos, límites, paginación, errores), las pruebas `tests_api.py`, el script `scripts/probar_api.py` y la documentación.

## U3.2 Recomendaciones de la IA, cómo se validaron y qué se decidió

Las propuestas y su contraste salieron de la misma sesión de trabajo con la IA (valores por defecto de las librerías, opciones habituales y lo que la IA propuso). La columna "Decisión" es la que debo revisar y poder defender yo.

| # | Propuesta o alternativa evaluada | Con qué se contrastó | Decisión y justificación |
|---|---|---|---|
| 1 | Autenticar con **JWT** (`djangorestframework-simplejwt`) | Documentación de DRF ("Authentication"), que ofrece `SessionAuthentication`, `TokenAuthentication` y paquetes JWT | **Aplicada.** La sesión con cookies sirve para el navegador pero obliga a manejar CSRF y no es práctica para apps móviles u otros servicios. `TokenAuthentication` entrega un token que no expira nunca. JWT expira solo y no guarda estado en el servidor, que es lo que pide REST. |
| 2 | `access` de 5 minutos (valor por defecto de la librería) | Uso real: un operador que registra paquetes durante su turno | **Adaptada a 15 minutos**, con `refresh` de 1 día. 5 minutos obliga a renovar constantemente; 15 mantiene corta la ventana si el token se filtra. |
| 3 | Rotar el `refresh` y ponerlo en lista negra | Pruebas `test_refresh_rota_el_token...` y `test_logout_deja_el_refresh_en_lista_negra` | **Aplicada.** Sin lista negra un "logout" en JWT no existe de verdad: el token seguiría sirviendo hasta expirar. Costo aceptado: una tabla extra y una consulta por renovación. |
| 4 | Exigir autenticación **por defecto** y marcar lo público a mano | Documentación de DRF ("Permissions"): el valor de fábrica es `AllowAny` | **Aplicada.** Con el valor de fábrica, olvidar una línea deja un endpoint abierto. Al revés, el olvido deja el endpoint cerrado, que es el error seguro. |
| 5 | Limitar intentos de login y de rastreo (throttling) | Prueba `test_login_se_bloquea_tras_demasiados_intentos` (el sexto intento responde 429) | **Aplicada**, con tasas propias: 5/min en login, 30/min en rastreo. |
| 6 | Agregar `django-cors-headers` | Arquitectura del proyecto: no hay un frontend en otro dominio | **Descartada.** Abrir CORS sin necesitarlo amplía quién puede llamar a la API desde un navegador. Se agregará, con lista de orígenes específica, solo si aparece un frontend separado. |
| 7 | Agregar `django-filter` para los filtros | Requerimiento real: un solo filtro (`?estado=`) | **Descartada.** Se resolvió con 6 líneas en `get_queryset` más los filtros de búsqueda y orden que ya trae DRF. Una dependencia menos que mantener y auditar. |
| 8 | Dejar la API navegable de DRF siempre activa | Documentación de DRF ("Renderers") | **Adaptada.** Solo con `DEBUG=True`. En producción la API responde únicamente JSON y solo acepta JWT. |
| 9 | Permitir que cualquier usuario autenticado elimine registros (`IsAuthenticated`) | Principio de mínimo privilegio; pruebas `test_eliminar_sin_ser_staff_responde_403` | **Adaptada.** Se creó el permiso `SoloStaffElimina`: DELETE solo para `is_staff`. |
| 10 | Reutilizar el serializer completo de `Paquete` en el rastreo público | Revisión de qué datos expone un endpoint sin autenticación | **Descartada.** Se creó `RastreoSerializer` con 5 campos, sin datos personales. Prueba: `test_rastreo_sin_token_muestra_solo_datos_minimos`. |

## U3.3 Problemas del código anterior que se detectaron al revisar

Estos tres vienen del código generado con IA en las unidades anteriores. Son el motivo por el que no basta con que "funcione":

1. **`.env.example` estaba guardado con BOM** (tres bytes invisibles al inicio del archivo). `python-dotenv` leía la primera variable como `﻿SECRET_KEY`, así que la `SECRET_KEY` del `.env` **nunca se cargaba** y el proyecto usaba en silencio la clave de respaldo escrita en el código, que es pública en GitHub. Con JWT esto es grave: quien conoce la clave puede fabricar tokens de cualquier usuario. Se reescribió el archivo sin BOM y ahora `settings.py` se niega a arrancar con `DEBUG=False` si no hay clave propia.
2. **El código de seguimiento se generaba con `random`**, que no es apto para seguridad (su secuencia se puede predecir). Como el código permite consultar un paquete sin iniciar sesión, se cambió por `secrets`.
3. **La contraseña del usuario de prueba estaba fija en el código** (`admin1234`). Ahora se lee de `.env` (`SEED_ADMIN_PASSWORD`), manteniendo ese valor solo como respaldo para desarrollo.

## U3.4 Riesgos identificados que NO están resueltos

- **Un `access` robado no se puede anular antes de que expire** (hasta 15 minutos). Es una limitación propia de JWT; se acepta a cambio de no consultar la base de datos en cada petición.
- **El throttling usa la caché en memoria de Django.** Los contadores se pierden al reiniciar el servidor y no se comparten entre procesos. En producción habría que configurar una caché compartida (Redis o Memcached).
- **El límite es por IP.** Muchos usuarios detrás de una misma red comparten cupo, y un atacante con muchas IP lo evade. Mitiga, no elimina.
- **El código de seguimiento tiene 6 caracteres** (36⁶ ≈ 2.176 millones de combinaciones). Con el límite de 30/min por IP no es viable recorrerlos, pero un código más largo sería más robusto.
- **Los JWT se firman con HS256 usando la `SECRET_KEY`.** Si la clave se filtra, se comprometen todos los tokens: hay que cambiarla y todos deben volver a iniciar sesión.
- **En local se trabaja sobre HTTP.** Las credenciales y tokens viajan sin cifrar; por eso `settings.py` fuerza HTTPS, HSTS y cookies seguras cuando `DEBUG=False`.
- **`admin / admin1234` es una clave débil** y solo debe existir en el computador de desarrollo.

## U3.5 Cómo se verificó (resultados reales)

- `python manage.py check` → sin errores. `python manage.py check --deploy` con `DEBUG=False` → solo dos avisos que no aplican (HSTS preload y backend de correo).
- `python manage.py test` → **39 pruebas, todas correctas** (32 de la API): autenticación, tokens inválidos, rotación, lista negra, bloqueo por intentos, CRUD, validaciones, permisos, códigos HTTP y formato JSON.
- `python scripts/probar_api.py` contra el servidor en ejecución → **34 de 34 peticiones** con el código HTTP esperado. Las respuestas reales están en `docs/PRUEBAS_ENDPOINTS.md`.

## U3.6 Lo que me corresponde a mí como estudiante

La IA escribió el código; entenderlo y poder defenderlo es responsabilidad mía. Antes de entregar:

1. Leer `paqueteria/api/` completo y poder explicar qué hace cada archivo.
2. Ejecutar yo mismo las peticiones de `docs/api.http` (o Postman) y tomar capturas de pantalla propias.
3. Poder explicar con mis palabras: qué es un JWT, la diferencia entre `access` y `refresh`, y por qué el logout necesita lista negra.
4. Revisar la tabla U3.2 y corregir cualquier decisión con la que no esté de acuerdo o que no sepa justificar.
5. Cambiar `SECRET_KEY` y la clave del usuario de prueba por valores propios en `.env`.
