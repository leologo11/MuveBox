from rest_framework.views import exception_handler

# Nombre corto y estable por código HTTP, para que el cliente de la API pueda
# reaccionar al tipo de error sin depender del texto del mensaje.
CODIGOS = {
    400: "solicitud_invalida",
    401: "no_autenticado",
    403: "sin_permiso",
    404: "no_encontrado",
    405: "metodo_no_permitido",
    415: "formato_no_soportado",
    429: "demasiadas_peticiones",
}


def cuerpo_error(status, mensaje, detalles=None):
    return {
        "error": {
            "codigo": CODIGOS.get(status, "error"),
            "mensaje": mensaje,
            "detalles": detalles or {},
        }
    }


def manejador_errores(exc, context):
    """Todos los errores de la API salen con la misma estructura JSON."""
    response = exception_handler(exc, context)
    if response is None:
        # Error no controlado: se deja que Django responda 500 sin exponer detalles.
        return None

    data = response.data
    if isinstance(data, dict) and set(data) <= {"detail", "code", "messages"}:
        # Error simple (401, 403, 404, 405, 429...)
        mensaje, detalles = str(data.get("detail", "")), {}
    else:
        # Error de validación: {campo: [mensajes]}
        mensaje, detalles = "Los datos enviados no son válidos.", data

    response.data = cuerpo_error(response.status_code, mensaje, detalles)
    return response
