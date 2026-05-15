"""Management command para cargar feriados mexicanos estándar 2024-2026."""

from django.core.management.base import BaseCommand
from holidays.models import Holiday
from datetime import date


class Command(BaseCommand):
    help = 'Seed holidays for Mexico for 2024-2026'

    def handle(self, *args, **options):
        """Carga feriados mexicanos usando get_or_create para evitar duplicados."""
        holidays = [
            (2024, 1, 1, 'Año Nuevo'),
            (2024, 2, 5, 'Día de la Constitución'),
            (2024, 3, 18, 'Natalicio de Benito Juárez'),
            (2024, 5, 1, 'Día del Trabajo'),
            (2024, 9, 16, 'Día de la Independencia'),
            (2024, 10, 12, 'Día de la Raza'),
            (2024, 11, 18, 'Día de la Revolución'),
            (2024, 12, 25, 'Navidad'),
            (2025, 1, 1, 'Año Nuevo'),
            (2025, 2, 3, 'Día de la Constitución'),
            (2025, 3, 17, 'Natalicio de Benito Juárez'),
            (2025, 5, 1, 'Día del Trabajo'),
            (2025, 9, 15, 'Grito de Dolores'),
            (2025, 10, 12, 'Día de la Raza'),
            (2025, 11, 17, 'Día de la Revolución'),
            (2025, 12, 25, 'Navidad'),
            (2026, 1, 1, 'Año Nuevo'),
            (2026, 2, 2, 'Día de la Constitución'),
            (2026, 3, 16, 'Natalicio de Benito Juárez'),
            (2026, 5, 1, 'Día del Trabajo'),
            (2026, 9, 15, 'Grito de Dolores'),
            (2026, 10, 12, 'Día de la Raza'),
            (2026, 11, 16, 'Día de la Revolución'),
            (2026, 12, 25, 'Navidad'),
        ]

        for year, month, day, desc in holidays:
            Holiday.objects.get_or_create(
                fecha=date(year, month, day),
                defaults={'descripcion': desc, 'activo': True}
            )

        self.stdout.write(self.style.SUCCESS(f'Loaded {len(holidays)} holidays'))