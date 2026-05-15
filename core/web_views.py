"""Vistas web del dashboard para Admin, Manager y Colaborador."""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import date, timedelta
from employees.models import User, Branch, Employee
from requests.models import Request
from absences.models import Absence, AbsenceAudit
from absences.forms import AbsenceForm
from holidays.models import Holiday
from .reports import generate_excel_report


def login_view(request):
    """Vista de autenticación por sesión para el dashboard web."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Credenciales incorrectas')
    return render(request, 'login.html')


def logout_view(request):
    """Cierra la sesión del usuario y redirige al login."""
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    """Dashboard principal con métricas operativas según rol del usuario.

    Admin/Manager: KPIs globales, solicitudes pendientes, calendario
    Colaborador: Perfil personal, saldo de vacaciones, últimas solicitudes
    """
    user = request.user

    if user.role in ['admin', 'manager']:
        if user.role == 'admin':
            branches = Branch.objects.all()
            employees = Employee.objects.filter(status='activo')
            solicitudes_pendientes = Request.objects.filter(estatus='pendiente')
        else:
            branches = user.branch_set.all()
            employees = Employee.objects.filter(branch__in=branches, status='activo')
            solicitudes_pendientes = Request.objects.filter(empleado__branch__in=branches, estatus='pendiente')

        absences_week = Absence.objects.filter(
            fecha__gte=date.today() - timedelta(days=7)
        ).count()

        first_day_month = date.today().replace(day=1)
        absences_month = Absence.objects.filter(fecha__gte=first_day_month).count()
        requests_month = Request.objects.filter(created_at__date__gte=first_day_month).count()
        vacations_approved = Request.objects.filter(
            tipo='vacacion', estatus='aprobado', updated_at__date__gte=first_day_month
        ).count()

        context = {
            'branches': branches,
            'employees_count': employees.count(),
            'solicitudes_pendientes': solicitudes_pendientes,
            'absences_week': absences_week,
            'absences_month': absences_month,
            'requests_month': requests_month,
            'vacations_approved': vacations_approved,
        }
        return render(request, 'dashboard_admin.html', context)
    else:
        try:
            employee = user.employee
            solicitudes = Request.objects.filter(empleado=employee)[:5]
            context = {
                'employee': employee,
                'solicitudes': solicitudes,
            }
        except Employee.DoesNotExist:
            context = {}
        return render(request, 'dashboard_user.html', context)


@login_required
def empleados_view(request):
    """Lista de empleados con búsqueda por nombre, número y CURP.

    Resultados paginados (20 por página) con navegación.
    """
    user = request.user
    search = request.GET.get('search', '')
    page = request.GET.get('page', 1)

    if user.role == 'admin':
        queryset = Employee.objects.all()
    else:
        queryset = Employee.objects.filter(branch__in=user.branch_set.all())

    if search:
        queryset = queryset.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(employee_number__icontains=search) |
            Q(curp__icontains=search)
        )

    empleados_qs = queryset.order_by('employee_number')
    paginator = Paginator(empleados_qs, 20)
    empleados = paginator.get_page(page)

    return render(request, 'empleados.html', {
        'empleados': empleados,
        'search': search,
        'total': paginator.count,
    })


@login_required
def solicitudes_view(request):
    """Lista de solicitudes con filtros por estatus y tipo.

    Resultados paginados (25 por página) con navegación.
    """
    user = request.user
    status_filter = request.GET.get('status', '')
    tipo_filter = request.GET.get('tipo', '')
    page = request.GET.get('page', 1)

    if user.role == 'admin':
        queryset = Request.objects.all()
    else:
        queryset = Request.objects.filter(empleado__branch__in=user.branch_set.all())

    if status_filter:
        queryset = queryset.filter(estatus=status_filter)
    if tipo_filter:
        queryset = queryset.filter(tipo=tipo_filter)

    solicitudes_qs = queryset.order_by('-created_at')
    paginator = Paginator(solicitudes_qs, 25)
    solicitudes = paginator.get_page(page)

    return render(request, 'solicitudes.html', {
        'solicitudes': solicitudes,
        'status_filter': status_filter,
        'tipo_filter': tipo_filter,
    })


@login_required
def solicitudes_pendientes_view(request):
    """Panel de aprobación rápida para solicitudes pendientes.

    Permite aprobar o rechazar con comentario opcional.
    Al aprobar vacaciones, descuenta automáticamente del saldo.
    """
    if request.user.role not in ['admin', 'manager']:
        return redirect('dashboard')

    if request.user.role == 'admin':
        solicitudes = Request.objects.filter(estatus='pendiente')
    else:
        solicitudes = Request.objects.filter(
            empleado__branch__in=request.user.branch_set.all(),
            estatus='pendiente'
        )

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        comentario = request.POST.get('comentario', '')

        try:
            req = Request.objects.get(id=request_id)
            req.estatus = 'aprobado' if action == 'approve' else 'rechazado'
            req.comentario_admin = comentario
            req.save()

            if action == 'approve' and req.tipo == 'vacacion':
                dias = req.dias_solicitados()
                req.empleado.saldo_vacaciones -= dias
                req.empleado.save()

            messages.success(request, f'Solicitud #{request_id} {req.get_estatus_display().lower()}')
        except Request.DoesNotExist:
            messages.error(request, 'Solicitud no encontrada')

        return redirect('solicitudes_pendientes')

    return render(request, 'solicitudes_pendientes.html', {'solicitudes': solicitudes})


@login_required
def ausencias_view(request):
    """Historial de inasistencias con filtros por sucursal, tipo y fecha.

    Resultados paginados (25 por página) con navegación.
    """
    if request.user.role not in ['admin', 'manager']:
        return redirect('dashboard')

    user = request.user
    search = request.GET.get('search', '')
    sucursal_id = request.GET.get('sucursal', '')
    tipo = request.GET.get('tipo', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    page = request.GET.get('page', 1)

    if user.role == 'admin':
        queryset = Absence.objects.all()
        branches = Branch.objects.all()
    else:
        branches = user.branch_set.all()
        queryset = Absence.objects.filter(sucursal__in=branches)

    if search:
        queryset = queryset.filter(
            Q(empleado__user__first_name__icontains=search) |
            Q(empleado__user__last_name__icontains=search) |
            Q(empleado__employee_number__icontains=search)
        )
    if sucursal_id:
        queryset = queryset.filter(sucursal_id=sucursal_id)
    if tipo:
        queryset = queryset.filter(tipo=tipo)
    if fecha_inicio:
        queryset = queryset.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha__lte=fecha_fin)

    ausencias_qs = queryset.order_by('-fecha')
    paginator = Paginator(ausencias_qs, 25)
    ausencias = paginator.get_page(page)

    context = {
        'ausencias': ausencias,
        'branches': branches,
        'search': search,
        'selected_sucursal': int(sucursal_id) if sucursal_id else '',
        'selected_tipo': tipo,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'types': Absence.TYPE_CHOICES
    }

    return render(request, 'ausencias.html', context)


@login_required
def registrar_ausencia(request):
    """Formulario de registro de inasistencia para Manager/Admin.

    Crea automáticamente un registro de auditoría al guardar.
    """
    if request.user.role not in ['admin', 'manager']:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AbsenceForm(request.POST, user=request.user)
        if form.is_valid():
            ausencia = form.save(commit=False)
            ausencia.registrado_por = request.user
            ausencia.save()

            AbsenceAudit.objects.create(
                absence=ausencia,
                action='create',
                changed_by=request.user
            )

            messages.success(request, 'Ausencia registrada correctamente')
            return redirect('ausencias')
    else:
        form = AbsenceForm(user=request.user)

    return render(request, 'registrar_ausencia.html', {'form': form})


@login_required
def sucursales_view(request):
    """Lista de sucursales. Acceso exclusivo para Admin."""
    if request.user.role != 'admin':
        return redirect('dashboard')

    branches = Branch.objects.all()
    return render(request, 'sucursales.html', {'sucursales': branches})


@login_required
def reportes_view(request):
    """Página de reportes con enlaces a exportación Excel."""
    if request.user.role != 'admin':
        return redirect('dashboard')

    return render(request, 'reportes.html')


@login_required
def exportar_vacaciones(request):
    """Exporta reporte de vacaciones por sucursal a Excel."""
    if request.user.role != 'admin':
        return redirect('dashboard')

    queryset = Employee.objects.all().order_by('branch', 'employee_number')
    headers = ['No. Empleado', 'Nombre', 'Sucursal', 'Fecha Ingreso', 'Antigüedad (años)', 'Saldo Vacaciones']

    def data_func(emp):
        return [
            emp.employee_number,
            emp.user.get_full_name(),
            emp.branch.name if emp.branch else "",
            emp.fecha_ingreso,
            emp.calcular_antiguedad(),
            emp.saldo_vacaciones
        ]

    return generate_excel_report(queryset, "reporte_vacaciones", headers, data_func)


@login_required
def exportar_permisos(request):
    """Exporta historial de permisos a Excel con estatus y observaciones."""
    if request.user.role != 'admin':
        return redirect('dashboard')

    queryset = Request.objects.filter(tipo='permiso').order_by('-created_at')
    headers = ['ID', 'Empleado', 'Sucursal', 'Inicio', 'Fin', 'Estatus', 'Fuera de Cond.', 'Creado el']

    def data_func(req):
        return [
            req.id,
            req.empleado.user.get_full_name(),
            req.empleado.branch.name if req.empleado.branch else "",
            req.fecha_inicio,
            req.fecha_fin,
            req.get_estatus_display(),
            "Sí" if req.fuera_de_condiciones else "No",
            req.created_at.strftime('%Y-%m-%d %H:%M')
        ]

    return generate_excel_report(queryset, "reporte_permisos", headers, data_func)


@login_required
def exportar_ausencias(request):
    """Exporta registro de inasistencias a Excel."""
    if request.user.role != 'admin':
        return redirect('dashboard')

    queryset = Absence.objects.all().order_by('-fecha')
    headers = ['Empleado', 'Sucursal', 'Fecha', 'Tipo', 'Motivo', 'Registrado por']

    def data_func(abs_obj):
        return [
            abs_obj.empleado.user.get_full_name(),
            abs_obj.sucursal.name if abs_obj.sucursal else "",
            abs_obj.fecha,
            abs_obj.get_tipo_display(),
            abs_obj.motivo,
            abs_obj.registrado_por.get_full_name() if abs_obj.registrado_por else ""
        ]

    return generate_excel_report(queryset, "reporte_ausencias", headers, data_func)


@login_required
def mi_perfil(request):
    """Panel de transparencia personal del empleado."""
    try:
        employee = request.user.employee
        solicitudes = Request.objects.filter(empleado=employee)
        return render(request, 'mi_perfil.html', {'employee': employee, 'solicitudes': solicitudes})
    except Employee.DoesNotExist:
        messages.error(request, 'No tienes perfil de empleado')
        return redirect('dashboard')


@login_required
def mis_solicitudes(request):
    """Historial completo de solicitudes del empleado."""
    try:
        employee = request.user.employee
        solicitudes = Request.objects.filter(empleado=employee).order_by('-created_at')
        return render(request, 'mis_solicitudes.html', {'solicitudes': solicitudes})
    except Employee.DoesNotExist:
        return redirect('dashboard')


@login_required
def nueva_solicitud(request):
    """Formulario para crear nueva solicitud de vacaciones o permiso."""
    if request.method == 'POST':
        try:
            employee = request.user.employee
            tipo = request.POST.get('tipo')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            fuera_de_condiciones = request.POST.get('fuera_de_condiciones', 'off') == 'on'

            Request.objects.create(
                tipo=tipo,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                empleado=employee,
                fuera_de_condiciones=fuera_de_condiciones
            )

            messages.success(request, 'Solicitud creada correctamente')
            return redirect('mis_solicitudes')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    try:
        employee = request.user.employee
        return render(request, 'nueva_solicitud.html', {'employee': employee})
    except Employee.DoesNotExist:
        return redirect('dashboard')