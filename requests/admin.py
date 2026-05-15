from django.contrib import admin
from .models import Request, RequestComment


class RequestCommentInline(admin.TabularInline):
    model = RequestComment
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo', 'empleado', 'fecha_inicio', 'fecha_fin', 'estatus', 'fuera_de_condiciones', 'created_at']
    list_filter = ['estatus', 'tipo', 'fecha_inicio']
    search_fields = ['empleado__user__first_name', 'empleado__user__last_name', 'empleado__employee_number']
    inlines = [RequestCommentInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RequestComment)
class RequestCommentAdmin(admin.ModelAdmin):
    list_display = ['request', 'author', 'created_at']
    search_fields = ['contenido']