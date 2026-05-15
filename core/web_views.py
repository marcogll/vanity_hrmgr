from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import date, timedelta
from employees.models import User, Branch, Employee
from requests.models import Request
from absences.models import Absence
from holidays.models import Holiday


def login_view(request):
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
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
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

        context = {
            'branches': branches,
            'employees_count': employees.count(),
            'solicitudes_pendientes': solicitudes_pendientes,
            'absences_week': absences_week,
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
    user = request.user
    search = request.GET.get('search', '')

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

    empleados = queryset.order_by('employee_number')
    return render(request, 'empleados.html', {'empleados': empleados, 'search': search})


@login_required
def solicitudes_view(request):
    user = request.user
    status_filter = request.GET.get('status', '')
    tipo_filter = request.GET.get('tipo', '')

    if user.role == 'admin':
        queryset = Request.objects.all()
    else:
        queryset = Request.objects.filter(empleado__branch__in=user.branch_set.all())

    if status_filter:
        queryset = queryset.filter(estatus=status_filter)
    if tipo_filter:
        queryset = queryset.filter(tipo=tipo_filter)

    solicitudes = queryset.order_by('-created_at')[:50]
    return render(request, 'solicitudes.html', {'solicitudes': solicitudes})


@login_required
def solicitudes_pendientes_view(request):
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
    if request.user.role not in ['admin', 'manager']:
        return redirect('dashboard')

    if request.user.role == 'admin':
        ausencia_list = Absence.objects.all()[:50]
    else:
        ausencia_list = Absence.objects.filter(sucursal__in=request.user.branch_set.all())[:50]

    return render(request, 'ausencias.html', {'ausencias': ausencia_list})


@login_required
def sucursales_view(request):
    if request.user.role != 'admin':
        return redirect('dashboard')

    branches = Branch.objects.all()
    return render(request, 'sucursales.html', {'sucursales': branches})


@login_required
def reportes_view(request):
    if request.user.role != 'admin':
        return redirect('dashboard')

    return render(request, 'reportes.html')


@login_required
def mi_perfil(request):
    try:
        employee = request.user.employee
        solicitudes = Request.objects.filter(empleado=employee)
        return render(request, 'mi_perfil.html', {'employee': employee, 'solicitudes': solicitudes})
    except Employee.DoesNotExist:
        messages.error(request, 'No tienes perfil de empleado')
        return redirect('dashboard')


@login_required
def mis_solicitudes(request):
    try:
        employee = request.user.employee
        solicitudes = Request.objects.filter(empleado=employee).order_by('-created_at')
        return render(request, 'mis_solicitudes.html', {'solicitudes': solicitudes})
    except Employee.DoesNotExist:
        return redirect('dashboard')


@login_required
def nueva_solicitud(request):
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