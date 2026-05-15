"""Clases de permisos personalizados para RBAC en la API REST."""

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permite acceso exclusivo a usuarios con rol admin."""
    def has_permission(self, request, view):
        """Verifica que el usuario esté autenticado y tenga rol admin."""
        return request.user.is_authenticated and request.user.role == 'admin'


class IsManager(permissions.BasePermission):
    """Permite acceso exclusivo a usuarios con rol manager."""
    def has_permission(self, request, view):
        """Verifica que el usuario esté autenticado y tenga rol manager."""
        return request.user.is_authenticated and request.user.role == 'manager'


class IsAdminOrManager(permissions.BasePermission):
    """Permite acceso a usuarios con rol admin o manager."""
    def has_permission(self, request, view):
        """Verifica que el usuario esté autenticado y tenga rol admin o manager."""
        return request.user.is_authenticated and request.user.role in ['admin', 'manager']