from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Branch, Employee, EmployeeAudit


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('role', 'telegram_chat_id')}),
    )


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'active', 'created_at']
    list_filter = ['active']
    search_fields = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_number', 'user', 'branch', 'tipo_contrato', 'status', 'saldo_vacaciones']
    list_filter = ['status', 'tipo_contrato', 'branch']
    search_fields = ['employee_number', 'user__first_name', 'user__last_name', 'curp', 'rfc']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmployeeAudit)
class EmployeeAuditAdmin(admin.ModelAdmin):
    list_display = ['employee', 'action', 'field_changed', 'changed_by', 'created_at']
    list_filter = ['action']
    readonly_fields = ['created_at']