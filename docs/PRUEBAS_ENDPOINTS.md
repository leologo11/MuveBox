# Evidencia de pruebas de los endpoints

Generado por `python scripts/probar_api.py` el 12-10-2026 14:03 contra `http://127.0.0.1:8000`.

**Resultado: 34 de 34 peticiones respondieron con el código HTTP esperado.**

Las contraseñas y los tokens aparecen ocultos o recortados a propósito.

### Raíz de la API (pública)

`GET /api/v1/`  · sin token

Respuesta: **HTTP 200** ✅

```json
{
  "nombre": "MuveBox API",
  "version": "v1",
  "autenticacion": {
    "tipo": "JWT (cabecera Authorization: Bearer <access>)",
    "obtener_token": "http://127.0.0.1:8000/api/v1/auth/token/",
    "renovar_token": "http://127.0.0.1:8000/api/v1/auth/token/refresh/",
    "cerrar_sesion": "http://127.0.0.1:8000/api/v1/auth/logout/",
    "usuario_actual": "http://127.0.0.1:8000/api/v1/auth/me/"
  },
  "recursos": {
    "clientes": "http://127.0.0.1:8000/api/v1/clientes/",
    "paquetes": "http://127.0.0.1:8000/api/v1/paquetes/",
    "resumen_paquetes": "http://127.0.0.1:8000/api/v1/paquetes/resumen/",
    "rastreo_publico": "http://127.0.0.1:8000/api/v1/rastreo/MUV-XXXXXX/"
  }
}
```

### Endpoint protegido sin token

`GET /api/v1/paquetes/`  · sin token

Respuesta: **HTTP 401** ✅

```json
{
  "error": {
    "codigo": "no_autenticado",
    "mensaje": "Las credenciales de autenticación no se proveyeron.",
    "detalles": {}
  }
}
```

### Login con contraseña incorrecta

`POST /api/v1/auth/token/`  · sin token

Cuerpo enviado:
```json
{
  "username": "admin",
  "password": "********"
}
```
Respuesta: **HTTP 401** ✅

```json
{
  "error": {
    "codigo": "no_autenticado",
    "mensaje": "No active account found with the given credentials",
    "detalles": {}
  }
}
```

### Login correcto: entrega tokens JWT

`POST /api/v1/auth/token/`  · sin token

Cuerpo enviado:
```json
{
  "username": "admin",
  "password": "********"
}
```
Respuesta: **HTTP 200** ✅

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs...(recortado)",
  "access": "eyJhbGciOiJIUzI1NiIs...(recortado)"
}
```

### Token inválido

`GET /api/v1/paquetes/`  · con token

Respuesta: **HTTP 401** ✅

```json
{
  "error": {
    "codigo": "no_autenticado",
    "mensaje": "Given token not valid for any token type",
    "detalles": {}
  }
}
```

### Usuario dueño del token

`GET /api/v1/auth/me/`  · con token

Respuesta: **HTTP 200** ✅

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@muvebox.local",
  "first_name": "",
  "last_name": "",
  "is_staff": true
}
```

### Listar clientes (paginado)

`GET /api/v1/clientes/?page_size=2`  · con token

Respuesta: **HTTP 200** ✅

```json
{
  "total": 10,
  "paginas": 5,
  "pagina_actual": 1,
  "siguiente": "http://127.0.0.1:8000/api/v1/clientes/?page=2&page_size=2",
  "anterior": null,
  "resultados": [
    {
      "id": 8,
      "nombre": "Alejandra Leonor Córdova Barros",
      "email": "carlosmella@example.net",
      "telefono": "+56 45 261 4928",
      "direccion": "Avenida Janet Reyes 52, Talca, Región del Maule",
      "fecha_registro": "2026-10-12T14:03:26.681977-03:00",
      "total_enviados": 2,
      "total_recibidos": 2
    },
    {
      "id": 1,
      "nombre": "Alonso Lucas Catalán Serrano",
      "email": "enzo27@example.com",
      "telefono": "+56 600 842 457",
      "direccion": "Psje. Arturo Alessandri Palma 1109 Of. 7038, Ñuñoa, Región Metropolitana, 9242250",
      "fecha_registro": "2026-10-12T14:03:26.673436-03:00",
      "total_enviados": 1,
      "total_recibidos": 3
    }
  ]
}
```

### Crear cliente

`POST /api/v1/clientes/`  · con token

Cuerpo enviado:
```json
{
  "nombre": "Cliente Prueba Uno",
  "email": "uno1791824613@prueba.cl",
  "telefono": "+56 9 1234 5678"
}
```
Respuesta: **HTTP 201** ✅

```json
{
  "id": 11,
  "nombre": "Cliente Prueba Uno",
  "email": "uno1791824613@prueba.cl",
  "telefono": "+56 9 1234 5678",
  "direccion": "",
  "fecha_registro": "2026-10-12T14:03:35.736044-03:00",
  "total_enviados": 0,
  "total_recibidos": 0
}
```

### Crear segundo cliente

`POST /api/v1/clientes/`  · con token

Cuerpo enviado:
```json
{
  "nombre": "Cliente Prueba Dos",
  "email": "dos1791824613@prueba.cl"
}
```
Respuesta: **HTTP 201** ✅

```json
{
  "id": 12,
  "nombre": "Cliente Prueba Dos",
  "email": "dos1791824613@prueba.cl",
  "telefono": "",
  "direccion": "",
  "fecha_registro": "2026-10-12T14:03:35.745546-03:00",
  "total_enviados": 0,
  "total_recibidos": 0
}
```

### Crear cliente con email repetido (validación)

`POST /api/v1/clientes/`  · con token

Cuerpo enviado:
```json
{
  "nombre": "Repetido",
  "email": "uno1791824613@prueba.cl"
}
```
Respuesta: **HTTP 400** ✅

```json
{
  "error": {
    "codigo": "solicitud_invalida",
    "mensaje": "Los datos enviados no son válidos.",
    "detalles": {
      "email": [
        "Ya existe cliente con este email."
      ]
    }
  }
}
```

### Detalle de cliente

`GET /api/v1/clientes/11/`  · con token

Respuesta: **HTTP 200** ✅

```json
{
  "id": 11,
  "nombre": "Cliente Prueba Uno",
  "email": "uno1791824613@prueba.cl",
  "telefono": "+56 9 1234 5678",
  "direccion": "",
  "fecha_registro": "2026-10-12T14:03:35.736044-03:00",
  "total_enviados": 0,
  "total_recibidos": 0
}
```

### Reemplazar cliente (PUT)

`PUT /api/v1/clientes/11/`  · con token

Cuerpo enviado:
```json
{
  "nombre": "Cliente Prueba Uno Editado",
  "email": "uno1791824613@prueba.cl"
}
```
Respuesta: **HTTP 200** ✅

```json
{
  "id": 11,
  "nombre": "Cliente Prueba Uno Editado",
  "email": "uno1791824613@prueba.cl",
  "telefono": "+56 9 1234 5678",
  "direccion": "",
  "fecha_registro": "2026-10-12T14:03:35.736044-03:00",
  "total_enviados": 0,
  "total_recibidos": 0
}
```

### Modificar parcialmente cliente (PATCH)

`PATCH /api/v1/clientes/11/`  · con token

Cuerpo enviado:
```json
{
  "direccion": "Av. Providencia 1234, Santiago"
}
```
Respuesta: **HTTP 200** ✅

```json
{
  "id": 11,
  "nombre": "Cliente Prueba Uno Editado",
  "email": "uno1791824613@prueba.cl",
  "telefono": "+56 9 1234 5678",
  "direccion": "Av. Providencia 1234, Santiago",
  "fecha_registro": "2026-10-12T14:03:35.736044-03:00",
  "total_enviados": 0,
  "total_recibidos": 0
}
```

### Buscar clientes

`GET /api/v1/clientes/?search=Prueba+Dos`  · con token

Respuesta: **HTTP 200** ✅

```json
{
  "total": 1,
  "paginas": 1,
  "pagina_actual": 1,
  "siguiente": null,
  "anterior": null,
  "resultados": [
    {
      "id": 12,
      "nombre": "Cliente Prueba Dos",
      "email": "dos1791824613@prueba.cl",
      "telefono": "",
      "direccion": "",
      "fecha_registro": "2026-10-12T14:03:35.745546-03:00",
      "total_enviados": 0,
      "total_recibidos": 0
    }
  ]
}
```

### Crear paquete

`POST /api/v1/paquetes/`  · con token

Cuerpo enviado:
```json
{
  "remitente": 11,
  "destinatario": 12,
  "descripcion": "Caja de prueba",
  "peso_kg": "3.20",
  "direccion_entrega": "Los Aromos 456, Ñuñoa"
}
```
Respuesta: **HTTP 201** ✅

```json
{
  "id": 21,
  "codigo_seguimiento": "MUV-6L2DXS",
  "remitente": 11,
  "remitente_detalle": {
    "id": 11,
    "nombre": "Cliente Prueba Uno Editado",
    "email": "uno1791824613@prueba.cl"
  },
  "destinatario": 12,
  "destinatario_detalle": {
    "id": 12,
    "nombre": "Cliente Prueba Dos",
    "email": "dos1791824613@prueba.cl"
  },
  "descripcion": "Caja de prueba",
  "peso_kg": "3.20",
  "direccion_entrega": "Los Aromos 456, Ñuñoa",
  "estado": "PENDIENTE",
  "estado_descripcion": "Pendiente de retiro",
  "notas": "",
  "fecha_creacion": "2026-10-12T14:03:35.795505-03:00",
  "fecha_actualizacion": "2026-10-12T14:03:35.795505-03:00"
}
```

### Crear paquete inválido (peso negativo y mismo cliente)

`POST /api/v1/paquetes/`  · con token

Cuerpo enviado:
```json
{
  "remitente": 11,
  "destinatario": 11,
  "descripcion": "Mal",
  "peso_kg": "-5",
  "direccion_entrega": "X"
}
```
Respuesta: **HTTP 400** ✅

```json
{
  "error": {
    "codigo": "solicitud_invalida",
    "mensaje": "Los datos enviados no son válidos.",
    "detalles": {
      "peso_kg": [
        "El peso debe ser mayor que 0 kg."
      ]
    }
  }
}
```

### Detalle de paquete

`GET /api/v1/paquetes/21/`  · con token

Respuesta: **HTTP 200** ✅

```json
{
  "id": 21,
  "codigo_seguimiento": "MUV-6L2DXS",
  "remitente": 11,
  "remitente_detalle": {
    "id": 11,
    "nombre": "Cliente Prueba Uno Editado",
    "email": "uno1791824613@prueba.cl"
  },
  "destinatario": 12,
  "destinatario_detalle": {
    "id": 12,
    "nombre": "Cliente Prueba Dos",
    "email": "dos1791824613@prueba.cl"
  },
  "descripcion": "Caja de prueba",
  "peso_kg": "3.20",
  "direccion_entrega": "Los Aromos 456, Ñuñoa",
  "estado": "PENDIENTE",
  "estado_descripcion": "Pendiente de retiro",
  "notas": "",
  "fecha_creacion": "2026-10-12T14:03:35.795505-03:00",
  "fecha_actualizacion": "2026-10-12T14:03:35.795505-03:00"
}
```

### Cambiar estado del paquete (PATCH)

`PATCH /api/v1/paquetes/21/`  · con token

Cuerpo enviado:
```json
{
  "estado": "EN_TRANSITO"
}
```
Respuesta: **HTTP 200** ✅

```json
{
  "id": 21,
  "codigo_seguimiento": "MUV-6L2DXS",
  "remitente": 11,
  "remitente_detalle": {
    "id": 11,
    "nombre": "Cliente Prueba Uno Editado",
    "email": "uno1791824613@prueba.cl"
  },
  "destinatario": 12,
  "destinatario_detalle": {
    "id": 12,
    "nombre": "Cliente Prueba Dos",
    "email": "dos1791824613@prueba.cl"
  },
  "descripcion": "Caja de prueba",
  "peso_kg": "3.20",
  "direccion_entrega": "Los Aromos 456, Ñuñoa",
  "estado": "EN_TRANSITO",
  "estado_descripcion": "En tránsito",
  "notas": "",
  "fecha_creacion": "2026-10-12T14:03:35.795505-03:00",
  "fecha_actualizacion": "2026-10-12T14:03:35.820509-03:00"
}
```

### Listar paquetes filtrados por estado

`GET /api/v1/paquetes/?estado=EN_TRANSITO&page_size=2`  · con token

Respuesta: **HTTP 200** ✅

```json
{
  "total": 6,
  "paginas": 3,
  "pagina_actual": 1,
  "siguiente": "http://127.0.0.1:8000/api/v1/paquetes/?estado=EN_TRANSITO&page=2&page_size=2",
  "anterior": null,
  "resultados": [
    {
      "id": 21,
      "codigo_seguimiento": "MUV-6L2DXS",
      "remitente": 11,
      "remitente_detalle": {
        "id": 11,
        "nombre": "Cliente Prueba Uno Editado",
        "email": "uno1791824613@prueba.cl"
      },
      "destinatario": 12,
      "destinatario_detalle": {
        "id": 12,
        "nombre": "Cliente Prueba Dos",
        "email": "dos1791824613@prueba.cl"
      },
      "descripcion": "Caja de prueba",
      "peso_kg": "3.20",
      "direccion_entrega": "Los Aromos 456, Ñuñoa",
      "estado": "EN_TRANSITO",
      "estado_descripcion": "En tránsito",
      "notas": "",
      "fecha_creacion": "2026-10-12T14:03:35.795505-03:00",
      "fecha_actualizacion": "2026-10-12T14:03:35.820509-03:00"
    },
    {
      "id": 19,
      "codigo_seguimiento": "MUV-28COQ7",
      "remitente": 3,
      "remitente_detalle": {
        "id": 3,
        "nombre": "Giovanni Cristóbal Briones Márquez",
        "email": "jorgeyanez@example.com"
      },
      "destinatario": 1,
      "destinatario_detalle": {
        "id": 1,
        "nombre": "Alonso Lucas Catalán Serrano",
        "email": "enzo27@example.com"
      },
      "descripcion": "Set de herramientas",
      "peso_kg": "16.83",
      "direccion_entrega": "Psje. Arturo Prat 2590, Santiago, Región Metropolitana, 6845990",
      "estado": "EN_TRANSITO",
      "estado_descripcion": "En tránsito",
      "notas": "",
      "fecha_creacion": "2026-10-12T14:03:26.694782-03:00",
      "fecha_actualizacion": "2026-10-12T14:03:26.694782-03:00"
    }
  ]
}
```

### Filtro con estado inexistente

`GET /api/v1/paquetes/?estado=PERDIDO`  · con token

Respuesta: **HTTP 400** ✅

```json
{
  "error": {
    "codigo": "solicitud_invalida",
    "mensaje": "Los datos enviados no son válidos.",
    "detalles": {
      "estado": "Valor no válido. Opciones: PENDIENTE, EN_TRANSITO, ENTREGADO, CANCELADO."
    }
  }
}
```

### Resumen de paquetes por estado

`GET /api/v1/paquetes/resumen/`  · con token

Respuesta: **HTTP 200** ✅

```json
{
  "total": 21,
  "por_estado": {
    "PENDIENTE": 7,
    "EN_TRANSITO": 6,
    "ENTREGADO": 4,
    "CANCELADO": 4
  }
}
```

### Paquetes de un cliente

`GET /api/v1/clientes/11/paquetes/`  · con token

Respuesta: **HTTP 200** ✅

```json
{
  "total": 1,
  "paginas": 1,
  "pagina_actual": 1,
  "siguiente": null,
  "anterior": null,
  "resultados": [
    {
      "id": 21,
      "codigo_seguimiento": "MUV-6L2DXS",
      "remitente": 11,
      "remitente_detalle": {
        "id": 11,
        "nombre": "Cliente Prueba Uno Editado",
        "email": "uno1791824613@prueba.cl"
      },
      "destinatario": 12,
      "destinatario_detalle": {
        "id": 12,
        "nombre": "Cliente Prueba Dos",
        "email": "dos1791824613@prueba.cl"
      },
      "descripcion": "Caja de prueba",
      "peso_kg": "3.20",
      "direccion_entrega": "Los Aromos 456, Ñuñoa",
      "estado": "EN_TRANSITO",
      "estado_descripcion": "En tránsito",
      "notas": "",
      "fecha_creacion": "2026-10-12T14:03:35.795505-03:00",
      "fecha_actualizacion": "2026-10-12T14:03:35.820509-03:00"
    }
  ]
}
```

### Método no permitido

`POST /api/v1/paquetes/21/`  · con token

Cuerpo enviado:
```json
{}
```
Respuesta: **HTTP 405** ✅

```json
{
  "error": {
    "codigo": "metodo_no_permitido",
    "mensaje": "Método \"POST\" no permitido.",
    "detalles": {}
  }
}
```

### Rastreo público por código (sin token)

`GET /api/v1/rastreo/MUV-6L2DXS/`  · sin token

Respuesta: **HTTP 200** ✅

```json
{
  "codigo_seguimiento": "MUV-6L2DXS",
  "estado": "EN_TRANSITO",
  "estado_descripcion": "En tránsito",
  "fecha_creacion": "2026-10-12T14:03:35.795505-03:00",
  "fecha_actualizacion": "2026-10-12T14:03:35.820509-03:00"
}
```

### Rastreo de código inexistente

`GET /api/v1/rastreo/MUV-000000/`  · sin token

Respuesta: **HTTP 404** ✅

```json
{
  "error": {
    "codigo": "no_encontrado",
    "mensaje": "No Paquete matches the given query.",
    "detalles": {}
  }
}
```

### Ruta inexistente

`GET /api/v1/no-existe/`  · sin token

Respuesta: **HTTP 404** ✅

```json
{
  "error": {
    "codigo": "no_encontrado",
    "mensaje": "El recurso solicitado no existe. Revisa la ruta (todas terminan en '/').",
    "detalles": {}
  }
}
```

### Eliminar paquete

`DELETE /api/v1/paquetes/21/`  · con token

Respuesta: **HTTP 204** ✅

_(sin cuerpo)_

### Paquete eliminado ya no existe

`GET /api/v1/paquetes/21/`  · con token

Respuesta: **HTTP 404** ✅

```json
{
  "error": {
    "codigo": "no_encontrado",
    "mensaje": "No Paquete matches the given query.",
    "detalles": {}
  }
}
```

### Eliminar cliente

`DELETE /api/v1/clientes/11/`  · con token

Respuesta: **HTTP 204** ✅

_(sin cuerpo)_

### Eliminar segundo cliente

`DELETE /api/v1/clientes/12/`  · con token

Respuesta: **HTTP 204** ✅

_(sin cuerpo)_

### Renovar token (rota el refresh)

`POST /api/v1/auth/token/refresh/`  · sin token

Cuerpo enviado:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs...(recortado)"
}
```
Respuesta: **HTTP 200** ✅

```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...(recortado)",
  "refresh": "eyJhbGciOiJIUzI1NiIs...(recortado)"
}
```

### Reutilizar el refresh anterior (ya está en lista negra)

`POST /api/v1/auth/token/refresh/`  · sin token

Cuerpo enviado:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs...(recortado)"
}
```
Respuesta: **HTTP 401** ✅

```json
{
  "error": {
    "codigo": "no_autenticado",
    "mensaje": "Token is blacklisted",
    "detalles": {}
  }
}
```

### Cerrar sesión (invalida el refresh)

`POST /api/v1/auth/logout/`  · con token

Cuerpo enviado:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs...(recortado)"
}
```
Respuesta: **HTTP 204** ✅

_(sin cuerpo)_

### Renovar con el refresh de la sesión cerrada

`POST /api/v1/auth/token/refresh/`  · sin token

Cuerpo enviado:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs...(recortado)"
}
```
Respuesta: **HTTP 401** ✅

```json
{
  "error": {
    "codigo": "no_autenticado",
    "mensaje": "Token is blacklisted",
    "detalles": {}
  }
}
```
