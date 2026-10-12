from rest_framework.permissions import BasePermission


class SoloStaffElimina(BasePermission):
    """
    Cualquier usuario autenticado puede leer, crear y modificar,
    pero eliminar (DELETE) queda reservado al personal (is_staff).

    Principio de mínimo privilegio: borrar es la única operación que no se
    puede deshacer, así que se limita al rol con más responsabilidad.
    """

    message = "Solo el personal administrador puede eliminar registros."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method == "DELETE":
            return request.user.is_staff
        return True
