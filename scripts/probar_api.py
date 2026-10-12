"""
Prueba los endpoints de la API contra el servidor en ejecución y guarda la
evidencia (petición, código HTTP y respuesta JSON) en docs/PRUEBAS_ENDPOINTS.md.

Uso (con el servidor corriendo en otra terminal):
    python scripts/probar_api.py
    python scripts/probar_api.py --usuario admin --clave admin1234 --base http://127.0.0.1:8000

Solo usa la librería estándar de Python. Los registros que crea los elimina al final.
"""
import argparse
import json
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

SALIDA = Path(__file__).resolve().parent.parent / "docs" / "PRUEBAS_ENDPOINTS.md"


class Probador:
    def __init__(self, base):
        self.base = base.rstrip("/")
        self.token = None
        self.lineas = []
        self.fallas = 0

    def pedir(self, titulo, metodo, ruta, esperado, datos=None, auth=True, token=None):
        cabeceras = {"Accept": "application/json"}
        cuerpo = None
        if datos is not None:
            cuerpo = json.dumps(datos).encode()
            cabeceras["Content-Type"] = "application/json"
        token = token or (self.token if auth else None)
        if token:
            cabeceras["Authorization"] = f"Bearer {token}"
        peticion = urllib.request.Request(self.base + ruta, data=cuerpo, headers=cabeceras, method=metodo)
        try:
            with urllib.request.urlopen(peticion) as respuesta:
                status, texto = respuesta.status, respuesta.read().decode()
        except urllib.error.HTTPError as error:
            status, texto = error.code, error.read().decode()
        contenido = json.loads(texto) if texto else None

        ok = status == esperado
        self.fallas += 0 if ok else 1
        print(f"[{'OK' if ok else 'FALLA'}] {status} {metodo:6} {ruta}  ({titulo})")
        self.registrar(titulo, metodo, ruta, datos, status, esperado, contenido, bool(token))
        return contenido

    def registrar(self, titulo, metodo, ruta, datos, status, esperado, contenido, con_token):
        lineas = [f"### {titulo}", "", f"`{metodo} {ruta}`" + ("  · con token" if con_token else "  · sin token"), ""]
        if datos is not None:
            lineas += ["Cuerpo enviado:", "```json", json.dumps(ocultar(datos), indent=2, ensure_ascii=False), "```"]
        resultado = "✅" if status == esperado else f"❌ (se esperaba {esperado})"
        lineas += [f"Respuesta: **HTTP {status}** {resultado}", ""]
        if contenido is not None:
            lineas += ["```json", json.dumps(ocultar(contenido), indent=2, ensure_ascii=False), "```"]
        else:
            lineas += ["_(sin cuerpo)_"]
        self.lineas += lineas + [""]


def ocultar(dato):
    """No deja contraseñas ni tokens completos en el archivo de evidencia."""
    if isinstance(dato, dict):
        limpio = {}
        for clave, valor in dato.items():
            if clave == "password":
                limpio[clave] = "********"
            elif clave in ("access", "refresh") and isinstance(valor, str):
                limpio[clave] = valor[:20] + "...(recortado)"
            else:
                limpio[clave] = ocultar(valor)
        return limpio
    if isinstance(dato, list):
        return [ocultar(d) for d in dato[:2]] + (["... (más resultados)"] if len(dato) > 2 else [])
    return dato


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    parser.add_argument("--usuario", default="admin")
    parser.add_argument("--clave", default="admin1234")
    args = parser.parse_args()

    p = Probador(args.base)
    v1 = "/api/v1"
    marca = int(time.time())

    p.pedir("Raíz de la API (pública)", "GET", f"{v1}/", 200, auth=False)
    p.pedir("Endpoint protegido sin token", "GET", f"{v1}/paquetes/", 401, auth=False)
    p.pedir("Login con contraseña incorrecta", "POST", f"{v1}/auth/token/", 401,
            {"username": args.usuario, "password": "clave-incorrecta"}, auth=False)
    tokens = p.pedir("Login correcto: entrega tokens JWT", "POST", f"{v1}/auth/token/", 200,
                     {"username": args.usuario, "password": args.clave}, auth=False)
    if not tokens or "access" not in tokens:
        raise SystemExit("No se pudo iniciar sesión: revisa usuario/clave y que el servidor esté corriendo.")
    p.token = tokens["access"]

    p.pedir("Token inválido", "GET", f"{v1}/paquetes/", 401, token="token.falso.123")
    p.pedir("Usuario dueño del token", "GET", f"{v1}/auth/me/", 200)

    p.pedir("Listar clientes (paginado)", "GET", f"{v1}/clientes/?page_size=2", 200)
    c1 = p.pedir("Crear cliente", "POST", f"{v1}/clientes/", 201,
                 {"nombre": "Cliente Prueba Uno", "email": f"uno{marca}@prueba.cl", "telefono": "+56 9 1234 5678"})
    c2 = p.pedir("Crear segundo cliente", "POST", f"{v1}/clientes/", 201,
                 {"nombre": "Cliente Prueba Dos", "email": f"dos{marca}@prueba.cl"})
    p.pedir("Crear cliente con email repetido (validación)", "POST", f"{v1}/clientes/", 400,
            {"nombre": "Repetido", "email": f"uno{marca}@prueba.cl"})
    p.pedir("Detalle de cliente", "GET", f"{v1}/clientes/{c1['id']}/", 200)
    p.pedir("Reemplazar cliente (PUT)", "PUT", f"{v1}/clientes/{c1['id']}/", 200,
            {"nombre": "Cliente Prueba Uno Editado", "email": f"uno{marca}@prueba.cl"})
    p.pedir("Modificar parcialmente cliente (PATCH)", "PATCH", f"{v1}/clientes/{c1['id']}/", 200,
            {"direccion": "Av. Providencia 1234, Santiago"})
    p.pedir("Buscar clientes", "GET", f"{v1}/clientes/?search=Prueba+Dos", 200)

    paquete = p.pedir("Crear paquete", "POST", f"{v1}/paquetes/", 201,
                      {"remitente": c1["id"], "destinatario": c2["id"], "descripcion": "Caja de prueba",
                       "peso_kg": "3.20", "direccion_entrega": "Los Aromos 456, Ñuñoa"})
    p.pedir("Crear paquete inválido (peso negativo y mismo cliente)", "POST", f"{v1}/paquetes/", 400,
            {"remitente": c1["id"], "destinatario": c1["id"], "descripcion": "Mal",
             "peso_kg": "-5", "direccion_entrega": "X"})
    p.pedir("Detalle de paquete", "GET", f"{v1}/paquetes/{paquete['id']}/", 200)
    p.pedir("Cambiar estado del paquete (PATCH)", "PATCH", f"{v1}/paquetes/{paquete['id']}/", 200,
            {"estado": "EN_TRANSITO"})
    p.pedir("Listar paquetes filtrados por estado", "GET", f"{v1}/paquetes/?estado=EN_TRANSITO&page_size=2", 200)
    p.pedir("Filtro con estado inexistente", "GET", f"{v1}/paquetes/?estado=PERDIDO", 400)
    p.pedir("Resumen de paquetes por estado", "GET", f"{v1}/paquetes/resumen/", 200)
    p.pedir("Paquetes de un cliente", "GET", f"{v1}/clientes/{c1['id']}/paquetes/", 200)
    p.pedir("Método no permitido", "POST", f"{v1}/paquetes/{paquete['id']}/", 405, {})

    p.pedir("Rastreo público por código (sin token)", "GET",
            f"{v1}/rastreo/{paquete['codigo_seguimiento']}/", 200, auth=False)
    p.pedir("Rastreo de código inexistente", "GET", f"{v1}/rastreo/MUV-000000/", 404, auth=False)
    p.pedir("Ruta inexistente", "GET", f"{v1}/no-existe/", 404, auth=False)

    p.pedir("Eliminar paquete", "DELETE", f"{v1}/paquetes/{paquete['id']}/", 204)
    p.pedir("Paquete eliminado ya no existe", "GET", f"{v1}/paquetes/{paquete['id']}/", 404)
    p.pedir("Eliminar cliente", "DELETE", f"{v1}/clientes/{c1['id']}/", 204)
    p.pedir("Eliminar segundo cliente", "DELETE", f"{v1}/clientes/{c2['id']}/", 204)

    nuevos = p.pedir("Renovar token (rota el refresh)", "POST", f"{v1}/auth/token/refresh/", 200,
                     {"refresh": tokens["refresh"]}, auth=False)
    p.pedir("Reutilizar el refresh anterior (ya está en lista negra)", "POST", f"{v1}/auth/token/refresh/", 401,
            {"refresh": tokens["refresh"]}, auth=False)
    p.pedir("Cerrar sesión (invalida el refresh)", "POST", f"{v1}/auth/logout/", 204,
            {"refresh": nuevos["refresh"]})
    p.pedir("Renovar con el refresh de la sesión cerrada", "POST", f"{v1}/auth/token/refresh/", 401,
            {"refresh": nuevos["refresh"]}, auth=False)

    total = sum(1 for linea in p.lineas if linea.startswith("### "))
    encabezado = [
        "# Evidencia de pruebas de los endpoints",
        "",
        f"Generado por `python scripts/probar_api.py` el {datetime.now():%d-%m-%Y %H:%M} contra `{p.base}`.",
        "",
        f"**Resultado: {total - p.fallas} de {total} peticiones respondieron con el código HTTP esperado.**",
        "",
        "Las contraseñas y los tokens aparecen ocultos o recortados a propósito.",
        "",
    ]
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text("\n".join(encabezado + p.lineas), encoding="utf-8")
    print(f"\n{total - p.fallas}/{total} correctas. Evidencia guardada en {SALIDA}")
    raise SystemExit(1 if p.fallas else 0)


if __name__ == "__main__":
    main()
