"""Vistas para reportes y auditoría del sistema."""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from datetime import date, timedelta
from requests.models import Request
from absences.models import Absence, AbsenceAudit
from employees.models import EmployeeAudit


@login_required
def auditoria_view(request):
    """Panel de auditoría para Admin.

    Muestra logs de cambios en empleados, ausencias y solicitudes
    con filtros por tipo de acción y fecha.
    """
    if request.user.role != 'admin':
        return render(request, '403.html', status=403)

    action_filter = request.GET.get('action', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    employee_audits = EmployeeAudit.objects.select_related('employee', 'changed_by').all()
    absence_audits = AbsenceAudit.objects.select_related('absence', 'changed_by').all()

    if action_filter:
        employee_audits = employee_audits.filter(action=action_filter)
        absence_audits = absence_audits.filter(action=action_filter)
    if fecha_inicio:
        employee_audits = employee_audits.filter(created_at__date__gte=fecha_inicio)
        absence_audits = absence_audits.filter(created_at__date__gte=fecha_inicio)
    if fecha_fin:
        employee_audits = employee_audits.filter(created_at__date__lte=fecha_fin)
        absence_audits = absence_audits.filter(created_at__date__lte=fecha_fin)

    all_audits = sorted(
        list(employee_audits[:50]) + list(absence_audits[:50]),
        key=lambda x: x.created_at,
        reverse=True
    )[:100]

    context = {
        'audits': all_audits,
        'actions': EmployeeAudit.ACTION_CHOICES,
        'action_filter': action_filter,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }

    return render(request, 'auditoria.html', context)


@login_required
def metricas_view(request):
    """Vista de métricas operativas con gráficos para Admin.

    Genera datos para gráficos de:
    - Solicitudes por mes (últimos 12 meses)
    - Inasistencias por tipo
    - Indicadores de aprobación/rechazo
    """
    if request.user.role != 'admin':
        return render(request, '403.html', status=403)

    today = date.today()
    months = []
    requests_by_month = []
    absences_by_month = []

    for i in range(11, -1, -1):
        month_date = today - timedelta(days=30 * i)
        month_start = month_date.replace(day=1)
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)

        months.append(month_date.strftime('%b %Y'))
        requests_by_month.append(
            Request.objects.filter(created_at__date__range=[month_start, month_end]).count()
        )
        absences_by_month.append(
            Absence.objects.filter(fecha__range=[month_start, month_end]).count()
        )

    ausencias_por_tipo = dict(
        Absence.objects.values_list('tipo').annotate(count=Count('tipo')).order_by('-count')
    )

    solicitudes_estatus = {
        'pendiente': Request.objects.filter(estatus='pendiente').count(),
        'aprobado': Request.objects.filter(estatus='aprobado').count(),
        'rechazado': Request.objects.filter(estatus='rechazado').count(),
    }

    total = sum(solicitudes_estatus.values()) or 1
    tasa_aprobacion = round((solicitudes_estatus['aprobado'] / total) * 100, 1)
    tasa_rechazo = round((solicitudes_estatus['rechazado'] / total) * 100, 1)

    context = {
        'months': months,
        'requests_by_month': requests_by_month,
        'absences_by_month': absences_by_month,
        'ausencias_por_tipo': ausencias_por_tipo,
        'solicitudes_estatus': solicitudes_estatus,
        'tasa_aprobacion': tasa_aprobacion,
        'tasa_rechazo': tasa_rechazo,
    }

    return render(request, 'metricas.html', context)