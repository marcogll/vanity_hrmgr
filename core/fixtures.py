"""Fixtures para datos de prueba del sistema HR Manager.

Proporciona datos de ejemplo para:
- Usuarios con diferentes roles
- Sucursales
- Empleados
- Feriados
- Solicitudes
- Inasistencias
"""

import pytest
from datetime import date, timedelta
from employees.models import User, Branch, Employee
from holidays.models import Holiday
from requests.models import Request
from absences.models import Absence


@pytest.fixture
def admin_user():
    """Crea un usuario con rol de administrador."""
    return User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='testpass123',
        first_name='Admin',
        last_name='Test',
        role='admin'
    )


@pytest.fixture
def manager_user():
    """Crea un usuario con rol de gerente."""
    return User.objects.create_user(
        username='manager',
        email='manager@test.com',
        password='testpass123',
        first_name='Manager',
        last_name='Test',
        role='manager'
    )


@pytest.fixture
def employee_user():
    """Crea un usuario con rol de colaborador."""
    return User.objects.create_user(
        username='empleado',
        email='empleado@test.com',
        password='testpass123',
        first_name='Empleado',
        last_name='Test',
        role='user'
    )


@pytest.fixture
def branch():
    """Crea una sucursal de prueba."""
    return Branch.objects.create(
        name='Sucursal Test',
        address='Calle Test 123',
        active=True
    )


@pytest.fixture
def employee(employee_user, branch):
    """Crea un empleado de prueba con 2 años de antigüedad."""
    return Employee.objects.create(
        user=employee_user,
        employee_number='EMP001',
        curp='TEST123456HDFRRL09',
        rfc='TEST123456ABC',
        tipo_contrato='laboral',
        fecha_ingreso=date.today() - timedelta(days=730),
        saldo_vacaciones=8,
        branch=branch,
        status='activo'
    )


@pytest.fixture
def holidays():
    """Crea feriados de prueba para el año actual."""
    year = date.today().year
    return [
        Holiday.objects.create(fecha=date(year, 1, 1), descripcion='Año Nuevo', activo=True),
        Holiday.objects.create(fecha=date(year, 5, 1), descripcion='Día del Trabajo', activo=True),
        Holiday.objects.create(fecha=date(year, 9, 16), descripcion='Independencia', activo=True),
    ]


@pytest.fixture
def vacation_request(employee):
    """Crea una solicitud de vacaciones pendiente."""
    return Request.objects.create(
        tipo='vacacion',
        fecha_inicio=date.today() + timedelta(days=10),
        fecha_fin=date.today() + timedelta(days=12),
        estatus='pendiente',
        empleado=employee
    )


@pytest.fixture
def permission_request(employee):
    """Crea una solicitud de permiso pendiente."""
    return Request.objects.create(
        tipo='permiso',
        fecha_inicio=date.today() + timedelta(days=5),
        fecha_fin=date.today() + timedelta(days=5),
        estatus='pendiente',
        empleado=employee
    )


@pytest.fixture
def absence(employee, branch, admin_user):
    """Crea un registro de inasistencia."""
    return Absence.objects.create(
        empleado=employee,
        fecha=date.today() - timedelta(days=1),
        sucursal=branch,
        tipo='injustificada',
        motivo='No se presentó',
        registrado_por=admin_user
    )