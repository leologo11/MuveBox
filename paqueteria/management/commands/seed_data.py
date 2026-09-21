import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from paqueteria.models import Cliente, Paquete

DESCRIPCIONES = [
    "Caja de ropa", "Equipo electrónico", "Documentos", "Repuestos de bicicleta",
    "Libros usados", "Set de herramientas", "Artículos de cocina", "Juguetes",
    "Accesorios de oficina", "Calzado deportivo",
]


class Command(BaseCommand):
    help = (
        "Genera datos de prueba (clientes y paquetes) usando Faker, y un "
        "superusuario de desarrollo si no existe. Uso: python manage.py seed_data"
    )

    def add_arguments(self, parser):
        parser.add_argument("--clientes", type=int, default=10)
        parser.add_argument("--paquetes", type=int, default=20)

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker("es_CL")
        User = get_user_model()

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@muvebox.local", "admin1234")
            self.stdout.write(self.style.SUCCESS("Superusuario creado -> admin / admin1234"))
        else:
            self.stdout.write("Superusuario 'admin' ya existía, se omite.")

        clientes = []
        for _ in range(options["clientes"]):
            cliente, creado = Cliente.objects.get_or_create(
                email=fake.unique.email(),
                defaults={
                    "nombre": fake.name(),
                    "telefono": fake.phone_number(),
                    "direccion": fake.address().replace("\n", ", "),
                },
            )
            clientes.append(cliente)
        self.stdout.write(self.style.SUCCESS(f"Clientes disponibles: {Cliente.objects.count()}"))

        if len(clientes) < 2:
            self.stdout.write(self.style.WARNING("Se necesitan al menos 2 clientes para crear paquetes."))
            return

        estados = [e[0] for e in Paquete.Estado.choices]
        creados = 0
        for _ in range(options["paquetes"]):
            remitente, destinatario = random.sample(clientes, 2)
            Paquete.objects.create(
                remitente=remitente,
                destinatario=destinatario,
                descripcion=random.choice(DESCRIPCIONES),
                peso_kg=round(random.uniform(0.3, 25), 2),
                direccion_entrega=fake.address().replace("\n", ", "),
                estado=random.choice(estados),
                notas=fake.sentence() if random.random() > 0.5 else "",
            )
            creados += 1

        self.stdout.write(self.style.SUCCESS(f"Paquetes creados en esta ejecución: {creados}"))
        self.stdout.write(self.style.SUCCESS("Listo. Ejecuta 'python manage.py runserver' y entra con admin/admin1234"))
