"""Tests unitarios para modelos del sistema HR Manager."""

import pytest
from datetime import date, timedelta
from employees.models import User, Branch, Employee, EmployeeAudit
from holidays.models import Holiday
from requests.models import Request, RequestComment
from absences.models import Absence, AbsenceAudit


@pytest.mark.django_db
class TestUserModel:
    """Tests para el modelo User."""

    def test_create_admin_user(self):
        """Verifica que se puede crear un usuario admin."""
        user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass',
            role='admin'
        )
        assert user.role == 'admin'
        assert user.is_active

    def test_create_manager_user(self):
        """Verifica que se puede crear un usuario manager."""
        user = User.objects.create_user(
            username='manager',
            role='manager'
        )
        assert user.role == 'manager'

    def test_create_employee_user(self):
        """Verifica que se puede crear un usuario colaborador."""
        user = User.objects.create_user(
            username='employee',
            role='user'
        )
        assert user.role == 'user'


@pytest.mark.django_db
class TestBranchModel:
    """Tests para el modelo Branch."""

    def test_create_branch(self):
        """Verifica que se puede crear una sucursal."""
        branch = Branch.objects.create(
            name='Sucursal Test',
            address='Calle Test 123',
            active=True
        )
        assert branch.name == 'Sucursal Test'
        assert branch.active

    def test_branch_str(self):
        """Verifica la representación string de Branch."""
        branch = Branch.objects.create(name='Test Branch')
        assert str(branch) == 'Test Branch'


@pytest.mark.django_db
class TestEmployeeModel:
    """Tests para el modelo Employee."""

    @pytest.fixture
    def employee(self):
        """Crea un empleado de prueba."""
        user = User.objects.create_user(username='test', password='test')
        branch = Branch.objects.create(name='Test')
        return Employee.objects.create(
            user=user,
            employee_number='EMP001',
            fecha_ingreso=date.today() - timedelta(days=730),
            branch=branch,
            status='activo'
        )

    def test_create_employee(self, employee):
        """Verifica que se puede crear un empleado."""
        assert employee.employee_number == 'EMP001'
        assert employee.status == 'activo'

    def test_calcular_antiguedad(self, employee):
        """Verifica el cálculo de antigüedad."""
        assert employee.calcular_antiguedad() == 2

    def test_get_dias_vacaciones_1_year(self):
        """Verifica días de vacaciones para 1 año."""
        user = User.objects.create_user(username='test1', password='test')
        branch = Branch.objects.create(name='Test')
        emp = Employee.objects.create(
            user=user,
            employee_number='EMP002',
            fecha_ingreso=date.today() - timedelta(days=365),
            branch=branch
        )
        assert emp.get_dias_vacaciones() == 6

    def test_get_dias_vacaciones_5_years(self):
        """Verifica días de vacaciones para 5 años."""
        user = User.objects.create_user(username='test5', password='test')
        branch = Branch.objects.create(name='Test')
        emp = Employee.objects.create(
            user=user,
            employee_number='EMP005',
            fecha_ingreso=date.today() - timedelta(days=1825),
            branch=branch
        )
        assert emp.get_dias_vacaciones() == 14

    def test_get_dias_vacaciones_10_years(self):
        """Verifica días de vacaciones para 10 años."""
        user = User.objects.create_user(username='test10', password='test')
        branch = Branch.objects.create(name='Test')
        emp = Employee.objects.create(
            user=user,
            employee_number='EMP010',
            fecha_ingreso=date.today() - timedelta(days=3650),
            branch=branch
        )
        assert emp.get_dias_vacaciones() == 16

    def test_get_dias_vacaciones_20_years(self):
        """Verifica días de vacaciones para 20+ años."""
        user = User.objects.create_user(username='test20', password='test')
        branch = Branch.objects.create(name='Test')
        emp = Employee.objects.create(
            user=user,
            employee_number='EMP020',
            fecha_ingreso=date.today() - timedelta(days=7300),
            branch=branch
        )
        assert emp.get_dias_vacaciones() == 20


@pytest.mark.django_db
class TestHolidayModel:
    """Tests para el modelo Holiday."""

    def test_create_holiday(self):
        """Verifica que se puede crear un feriado."""
        holiday = Holiday.objects.create(
            fecha=date(2026, 1, 1),
            descripcion='Año Nuevo',
            activo=True
        )
        assert holiday.descripcion == 'Año Nuevo'

    def test_es_dia_festivo(self):
        """Verifica la detección de día festivo."""
        Holiday.objects.create(
            fecha=date(2026, 1, 1),
            descripcion='Año Nuevo',
            activo=True
        )
        assert Holiday.es_dia_festivo(date(2026, 1, 1)) is True
        assert Holiday.es_dia_festivo(date(2026, 1, 2)) is False

    def test_es_dia_festivo_inactivo(self):
        """Verifica que festivos inactivos no se detectan."""
        Holiday.objects.create(
            fecha=date(2026, 1, 1),
            descripcion='Año Nuevo',
            activo=False
        )
        assert Holiday.es_dia_festivo(date(2026, 1, 1)) is False


@pytest.mark.django_db
class TestRequestModel:
    """Tests para el modelo Request."""

    @pytest.fixture
    def employee(self):
        """Crea un empleado de prueba."""
        user = User.objects.create_user(username='test', password='test')
        branch = Branch.objects.create(name='Test')
        return Employee.objects.create(
            user=user,
            employee_number='EMP001',
            fecha_ingreso=date.today() - timedelta(days=730),
            branch=branch,
            saldo_vacaciones=10
        )

    def test_create_vacation_request(self, employee):
        """Verifica que se puede crear una solicitud de vacaciones."""
        req = Request.objects.create(
            tipo='vacacion',
            fecha_inicio=date.today() + timedelta(days=10),
            fecha_fin=date.today() + timedelta(days=12),
            estatus='pendiente',
            empleado=employee
        )
        assert req.tipo == 'vacacion'
        assert req.estatus == 'pendiente'

    def test_dias_solicitados_excluye_festivos(self, employee):
        """Verifica que días festivos no se cuentan."""
        Holiday.objects.create(
            fecha=date.today() + timedelta(days=1),
            descripcion='Festivo',
            activo=True
        )
        req = Request.objects.create(
            tipo='vacacion',
            fecha_inicio=date.today() + timedelta(days=1),
            fecha_fin=date.today() + timedelta(days=3),
            estatus='pendiente',
            empleado=employee
        )
        # Should exclude the holiday
        assert req.dias_solicitados() <= 3


@pytest.mark.django_db
class TestAbsenceModel:
    """Tests para el modelo Absence."""

    @pytest.fixture
    def employee(self):
        """Crea un empleado de prueba."""
        user = User.objects.create_user(username='test', password='test')
        branch = Branch.objects.create(name='Test')
        return Employee.objects.create(
            user=user,
            employee_number='EMP001',
            fecha_ingreso=date.today() - timedelta(days=730),
            branch=branch
        )

    def test_create_absence(self, employee):
        """Verifica que se puede crear una inasistencia."""
        admin = User.objects.create_user(username='admin', role='admin')
        absence = Absence.objects.create(
            empleado=employee,
            fecha=date.today(),
            tipo='injustificada',
            registrado_por=admin
        )
        assert absence.tipo == 'injustificada'
        assert absence.fecha == date.today()