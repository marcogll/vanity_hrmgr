from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.web_views import (
    login_view, logout_view, dashboard, empleados_view,
    solicitudes_view, solicitudes_pendientes_view, ausencias_view,
    sucursales_view, reportes_view, mi_perfil, mis_solicitudes,
    nueva_solicitud
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('empleados/', empleados_view, name='empleados'),
    path('solicitudes/', solicitudes_view, name='solicitudes'),
    path('solicitudes/pendientes/', solicitudes_pendientes_view, name='solicitudes_pendientes'),
    path('ausencias/', ausencias_view, name='ausencias'),
    path('sucursales/', sucursales_view, name='sucursales'),
    path('reportes/', reportes_view, name='reportes'),
    path('mi-perfil/', mi_perfil, name='mi_perfil'),
    path('mis-solicitudes/', mis_solicitudes, name='mis_solicitudes'),
    path('nueva-solicitud/', nueva_solicitud, name='nueva_solicitud'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)