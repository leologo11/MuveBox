from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClienteForm, PaqueteForm, RastreoForm
from .models import Cliente, Paquete


def home(request):
    """Dashboard simple con conteos por estado (MVC -> Controller)."""
    resumen = Paquete.objects.aggregate(
        total=Count("id"),
        pendientes=Count("id", filter=Q(estado=Paquete.Estado.PENDIENTE)),
        en_transito=Count("id", filter=Q(estado=Paquete.Estado.EN_TRANSITO)),
        entregados=Count("id", filter=Q(estado=Paquete.Estado.ENTREGADO)),
    )
    ultimos_paquetes = Paquete.objects.select_related("remitente", "destinatario")[:5]
    return render(
        request,
        "paqueteria/home.html",
        {"resumen": resumen, "ultimos_paquetes": ultimos_paquetes},
    )


def rastrear_paquete(request):
    """Vista pública: cualquier visitante puede rastrear un paquete por código."""
    paquete = None
    buscado = False
    if request.method == "POST":
        form = RastreoForm(request.POST)
        if form.is_valid():
            buscado = True
            codigo = form.cleaned_data["codigo_seguimiento"].strip().upper()
            paquete = Paquete.objects.filter(codigo_seguimiento=codigo).first()
    else:
        form = RastreoForm()
    return render(
        request,
        "paqueteria/rastrear.html",
        {"form": form, "paquete": paquete, "buscado": buscado},
    )


# ---------- CRUD de Paquete (requiere sesión iniciada) ----------

@login_required
def paquete_list(request):
    paquetes = Paquete.objects.select_related("remitente", "destinatario")
    query = request.GET.get("q", "").strip()
    if query:
        paquetes = paquetes.filter(
            Q(codigo_seguimiento__icontains=query)
            | Q(descripcion__icontains=query)
            | Q(remitente__nombre__icontains=query)
            | Q(destinatario__nombre__icontains=query)
        )
    estado = request.GET.get("estado", "").strip()
    if estado:
        paquetes = paquetes.filter(estado=estado)
    return render(
        request,
        "paqueteria/paquete_list.html",
        {
            "paquetes": paquetes,
            "query": query,
            "estado": estado,
            "estados": Paquete.Estado.choices,
        },
    )


@login_required
def paquete_detail(request, pk):
    paquete = get_object_or_404(
        Paquete.objects.select_related("remitente", "destinatario"), pk=pk
    )
    return render(request, "paqueteria/paquete_detail.html", {"paquete": paquete})


@login_required
def paquete_create(request):
    if request.method == "POST":
        form = PaqueteForm(request.POST)
        if form.is_valid():
            paquete = form.save()
            messages.success(request, f"Paquete {paquete.codigo_seguimiento} creado correctamente.")
            return redirect("paqueteria:paquete_detail", pk=paquete.pk)
    else:
        form = PaqueteForm()
    return render(
        request, "paqueteria/paquete_form.html", {"form": form, "titulo": "Nuevo paquete"}
    )


@login_required
def paquete_update(request, pk):
    paquete = get_object_or_404(Paquete, pk=pk)
    if request.method == "POST":
        form = PaqueteForm(request.POST, instance=paquete)
        if form.is_valid():
            form.save()
            messages.success(request, f"Paquete {paquete.codigo_seguimiento} actualizado.")
            return redirect("paqueteria:paquete_detail", pk=paquete.pk)
    else:
        form = PaqueteForm(instance=paquete)
    return render(
        request,
        "paqueteria/paquete_form.html",
        {"form": form, "titulo": f"Editar {paquete.codigo_seguimiento}"},
    )


@login_required
def paquete_delete(request, pk):
    paquete = get_object_or_404(Paquete, pk=pk)
    if request.method == "POST":
        codigo = paquete.codigo_seguimiento
        paquete.delete()
        messages.success(request, f"Paquete {codigo} eliminado.")
        return redirect("paqueteria:paquete_list")
    return render(request, "paqueteria/paquete_confirm_delete.html", {"paquete": paquete})


# ---------- CRUD de Cliente (requiere sesión iniciada) ----------

@login_required
def cliente_list(request):
    clientes = Cliente.objects.all()
    query = request.GET.get("q", "").strip()
    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) | Q(email__icontains=query)
        )
    return render(
        request, "paqueteria/cliente_list.html", {"clientes": clientes, "query": query}
    )


@login_required
def cliente_detail(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, "paqueteria/cliente_detail.html", {"cliente": cliente})


@login_required
def cliente_create(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f"Cliente {cliente.nombre} creado correctamente.")
            return redirect("paqueteria:cliente_detail", pk=cliente.pk)
    else:
        form = ClienteForm()
    return render(
        request, "paqueteria/cliente_form.html", {"form": form, "titulo": "Nuevo cliente"}
    )


@login_required
def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f"Cliente {cliente.nombre} actualizado.")
            return redirect("paqueteria:cliente_detail", pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)
    return render(
        request,
        "paqueteria/cliente_form.html",
        {"form": form, "titulo": f"Editar {cliente.nombre}"},
    )


@login_required
def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        nombre = cliente.nombre
        cliente.delete()
        messages.success(request, f"Cliente {nombre} eliminado.")
        return redirect("paqueteria:cliente_list")
    return render(request, "paqueteria/cliente_confirm_delete.html", {"cliente": cliente})
