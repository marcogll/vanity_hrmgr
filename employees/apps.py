"""Configuración de la app empleados: usuarios, sucursales y perfiles."""

from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    """App para gestión de empleados, sucursales y auditoría de cambios."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employees'
    verbose_name = 'Empleados y Sucursales'

    def ready(self):
        """Carga las señales de auditoría al iniciar la app."""
        import employees.signals