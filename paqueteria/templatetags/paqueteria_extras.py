from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Set de íconos propios (líneas simples, sin depender de librerías externas de íconos).
_ICONS = {
    "box": '<path d="M12 3 3 7.5 12 12l9-4.5L12 3Z"/><path d="M3 7.5V16l9 4.5V12"/><path d="M21 7.5V16l-9 4.5"/>',
    "search": '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "truck": '<path d="M3 7h11v9H3z"/><path d="M14 10h4l3 3v3h-7z"/><circle cx="7" cy="18" r="1.8"/><circle cx="17.5" cy="18" r="1.8"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.5 2.5L16 9.5"/>',
    "x-circle": '<circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/>',
    "user": '<circle cx="12" cy="8" r="3.5"/><path d="M4.5 20c1.5-4 4-6 7.5-6s6 2 7.5 6"/>',
    "users": '<circle cx="9" cy="8" r="3"/><path d="M2.5 20c1.2-3.5 3.3-5.3 6.5-5.3s5.3 1.8 6.5 5.3"/><circle cx="17" cy="9" r="2.4"/><path d="M15.5 14.2c2.4.3 4 1.8 5 5.8"/>',
    "plus": '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
    "edit": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    "trash": '<path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/>',
    "eye": '<path d="M1.5 12S5 5 12 5s10.5 7 10.5 7-3.5 7-10.5 7S1.5 12 1.5 12Z"/><circle cx="12" cy="12" r="3"/>',
    "arrow-right": '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="13 6 19 12 13 18"/>',
    "logout": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
    "package-search": '<path d="M12 3 3 7.5 12 12l9-4.5L12 3Z"/><path d="M3 7.5V16l6 3"/><path d="M21 7.5V13"/><circle cx="17.5" cy="17.5" r="3.2"/><line x1="19.8" y1="19.8" x2="22" y2="22"/>',
}


@register.simple_tag
def icon(name, size=20):
    body = _ICONS.get(name, "")
    return mark_safe(
        f'<svg class="mb-icon" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


_ESTADO_ICONS = {
    "PENDIENTE": "clock",
    "EN_TRANSITO": "truck",
    "ENTREGADO": "check-circle",
    "CANCELADO": "x-circle",
}


@register.simple_tag
def estado_icon(estado, size=16):
    return icon(_ESTADO_ICONS.get(estado, "clock"), size)


@register.filter
def estado_clase(estado):
    return {
        "PENDIENTE": "is-pending",
        "EN_TRANSITO": "is-transit",
        "ENTREGADO": "is-delivered",
        "CANCELADO": "is-cancelled",
    }.get(estado, "is-pending")
