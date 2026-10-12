from rest_framework.throttling import AnonRateThrottle


class LoginThrottle(AnonRateThrottle):
    """Limita los intentos de login por IP (tasa 'login' en settings)."""

    scope = "login"


class RastreoThrottle(AnonRateThrottle):
    """Limita el rastreo público, para que no se puedan adivinar códigos en masa."""

    scope = "rastreo"
