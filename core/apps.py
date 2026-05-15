"""Configuración de la app core: catálogos y utilidades centrales."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """App central para configuraciones globales y logs de notificaciones."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Catálogos y Configuración'