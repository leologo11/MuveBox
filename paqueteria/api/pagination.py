from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PaginacionEstandar(PageNumberPagination):
    """Paginación común a todos los listados: ?page=2&page_size=20."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100  # tope para que nadie pida la tabla completa de una vez

    def get_paginated_response(self, data):
        return Response(
            {
                "total": self.page.paginator.count,
                "paginas": self.page.paginator.num_pages,
                "pagina_actual": self.page.number,
                "siguiente": self.get_next_link(),
                "anterior": self.get_previous_link(),
                "resultados": data,
            }
        )
