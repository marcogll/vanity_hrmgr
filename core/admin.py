"""Administración del módulo core para configuraciones y logs."""

from django.contrib import admin
from .models import Configuration, NotificationLog


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    """Panel de administración para configuraciones globales del sistema."""
    list_display = ['key', 'value', 'description', 'updated_at']
    search_fields = ['key', 'description']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """Panel de auditoría para notificaciones enviadas por el sistema."""
    list_display = ['tipo', 'destinatario', 'estatus', 'created_at']
    list_filter = ['tipo', 'estatus']
    readonly_fields = ['created_at']