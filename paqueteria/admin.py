from django.contrib import admin

from .models import Cliente, Paquete

admin.site.site_header = "MuveBox · Administración"
admin.site.site_title = "MuveBox Admin"
admin.site.index_title = "Panel de gestión de paquetería"


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "telefono", "fecha_registro")
    search_fields = ("nombre", "email", "telefono")
    ordering = ("nombre",)


@admin.action(description="Marcar paquetes seleccionados como Entregado")
def marcar_como_entregado(modeladmin, request, queryset):
    actualizados = queryset.update(estado=Paquete.Estado.ENTREGADO)
    modeladmin.message_user(request, f"{actualizados} paquete(s) marcados como entregados.")


@admin.action(description="Marcar paquetes seleccionados como En tránsito")
def marcar_en_transito(modeladmin, request, queryset):
    actualizados = queryset.update(estado=Paquete.Estado.EN_TRANSITO)
    modeladmin.message_user(request, f"{actualizados} paquete(s) marcados como en tránsito.")


@admin.register(Paquete)
class PaqueteAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_seguimiento",
        "remitente",
        "destinatario",
        "estado",
        "peso_kg",
        "fecha_creacion",
    )
    list_filter = ("estado", "fecha_creacion")
    search_fields = (
        "codigo_seguimiento",
        "remitente__nombre",
        "destinatario__nombre",
        "descripcion",
    )
    autocomplete_fields = ("remitente", "destinatario")
    readonly_fields = ("codigo_seguimiento", "fecha_creacion", "fecha_actualizacion")
    actions = [marcar_como_entregado, marcar_en_transito]
