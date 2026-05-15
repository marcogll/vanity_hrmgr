"""Vistas API adicionales para dashboard y métricas."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from datetime import date, timedelta
from employees.models import Branch, Employee
from requests.models import Request
from absences.models import Absence


class DashboardAPIView(APIView):
    """Endpoint de dashboard con métricas operativas para Admin/Manager.

    Retorna KPIs agregados:
    - Conteo de sucursales, empleados activos
    - Solicitudes pendientes, aprobadas, rechazadas del mes
    - Inasistencias de la semana y mes
    - Distribución por tipo de ausencia
    - Top sucursales con más solicitudes
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna métricas operativas filtradas por rol del usuario.

        Admin: KPIs globales de todas las sucursales
        Manager: KPIs filtrados por sucursales asignadas
        User: Datos personales de vacaciones y solicitudes

        Returns:
            Response: Diccionario con métricas según rol
        """
        user = request.user
        first_day_month = date.today().replace(day=1)
        week_ago = date.today() - timedelta(days=7)

        if user.role == 'admin':
            branches = Branch.objects.all()
            employees = Employee.objects.filter(status='activo')
            requests_qs = Request.objects.all()
            absences_qs = Absence.objects.all()
        elif user.role == 'manager':
            user_branches = user.branch_set.all()
            branches = user_branches
            employees = Employee.objects.filter(branch__in=user_branches, status='activo')
            requests_qs = Request.objects.filter(empleado__branch__in=user_branches)
            absences_qs = Absence.objects.filter(sucursal__in=user_branches)
        else:
            try:
                employee = user.employee
                return Response({
                    'saldo_vacaciones': employee.saldo_vacaciones,
                    'antiguedad': employee.calcular_antiguedad(),
                    'dias_correspondientes': employee.get_dias_vacaciones(),
                    'solicitudes_pendientes': Request.objects.filter(empleado=employee, estatus='pendiente').count(),
                    'solicitudes_aprobadas': Request.objects.filter(empleado=employee, estatus='aprobado').count(),
                    'proxima_renovacion': employee.fecha_ingreso.strftime('%d de %B'),
                })
            except Employee.DoesNotExist:
                return Response({'error': 'No employee profile'}, status=404)

        solicitudes_mes = requests_qs.filter(created_at__date__gte=first_day_month)
        ausencias_semana = absences_qs.filter(fecha__gte=week_ago)
        ausencias_mes = absences_qs.filter(fecha__gte=first_day_month)

        data = {
            'sucursales': branches.count(),
            'empleados_activos': employees.count(),
            'solicitudes_pendientes': requests_qs.filter(estatus='pendiente').count(),
            'solicitudes_aprobadas_mes': solicitudes_mes.filter(estatus='aprobado').count(),
            'solicitudes_rechazadas_mes': solicitudes_mes.filter(estatus='rechazado').count(),
            'solicitudes_total_mes': solicitudes_mes.count(),
            'ausencias_semana': ausencias_semana.count(),
            'ausencias_mes': ausencias_mes.count(),
            'ausencias_por_tipo': dict(
                absences_qs.values_list('tipo').annotate(count=Count('tipo')).order_by('-count')
            ),
            'solicitudes_por_tipo': dict(
                requests_qs.values_list('tipo').annotate(count=Count('tipo')).order_by('-count')
            ),
        }

        if user.role == 'admin':
            data['top_sucursales_solicitudes'] = dict(
                requests_qs.values('empleado__branch__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
                .values_list('empleado__branch__name', 'count')
            )

        return Response(data)