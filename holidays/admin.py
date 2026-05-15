from django.contrib import admin
from .models import Holiday


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['descripcion']
    ordering = ['fecha']