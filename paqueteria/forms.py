from django import forms

from .models import Cliente, Paquete


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "email", "telefono", "direccion"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
        }


class PaqueteForm(forms.ModelForm):
    class Meta:
        model = Paquete
        fields = [
            "remitente",
            "destinatario",
            "descripcion",
            "peso_kg",
            "direccion_entrega",
            "estado",
            "notas",
        ]
        widgets = {
            "remitente": forms.Select(attrs={"class": "form-select"}),
            "destinatario": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.TextInput(attrs={"class": "form-control"}),
            "peso_kg": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "direccion_entrega": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "notas": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class RastreoForm(forms.Form):
    codigo_seguimiento = forms.CharField(
        max_length=15,
        label="Código de seguimiento",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ej: MUV-A1B2C3"}
        ),
    )
