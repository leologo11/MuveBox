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
