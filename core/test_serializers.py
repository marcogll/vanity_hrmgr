"""Tests para serializers y validaciones del sistema HR Manager."""

import pytest
from datetime import date, timedelta
from employees.models import User, Branch, Employee
from holidays.models import Holiday
from requests.serializers import RequestSerializer
from absences.serializers import AbsenceSerializer


@pytest.mark.django_db
class TestRequestSerializer:
    """Tests para el serializer de solicitudes."""

    @pytest.fixture
    def employee(self):
        """Crea un empleado con 10 días de vacaciones."""
        user = User.objects.create_user(username='test', password='test')
        branch = Branch.objects.create(name='Test')
        return Employee.objects.create(
            user=user,
            employee_number='EMP001',
            fecha_ingreso=date.today() - timedelta(days=730),
            branch=branch,
            saldo_vacaciones=10
        )

    def test_valid_vacation_request(self, employee):
        """Verifica que una solicitud de vacaciones válida pasa."""
        data = {
            'tipo': 'vacacion',
            'fecha_inicio': date.today() + timedelta(days=10),
            'fecha_fin': date.today() + timedelta(days=12),
            'empleado': employee.id
        }
        serializer = RequestSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_invalid_dates_order(self, employee):
        """Verifica que fecha_inicio posterior a fecha_fin falla."""
        data = {
            'tipo': 'vacacion',
            'fecha_inicio': date.today() + timedelta(days=10),
            'fecha_fin': date.today() + timedelta(days=5),
            'empleado': employee.id
        }
        serializer = RequestSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors

    def test_insufficient_vacation_balance(self, employee):
        """Verifica que saldo insuficiente falla sin bandera fuera_de_condiciones."""
        data = {
            'tipo': 'vacacion',
            'fecha_inicio': date.today() + timedelta(days=10),
            'fecha_fin': date.today() + timedelta(days=30),
            'empleado': employee.id
        }
        serializer = RequestSerializer(data=data)
        assert not serializer.is_valid()

    def test_vacation_with_out_of_conditions_flag(self, employee):
        """Verifica que fuera_de_condiciones permite solicitud sin saldo."""
        data = {
            'tipo': 'vacacion',
            'fecha_inicio': date.today() + timedelta(days=10),
            'fecha_fin': date.today() + timedelta(days=30),
            'empleado': employee.id,
            'fuera_de_condiciones': True
        }
        serializer = RequestSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_permission_max_3_days(self, employee):
        """Verifica que permisos mayores a 3 días fallan."""
        data = {
            'tipo': 'permiso',
            'fecha_inicio': date.today() + timedelta(days=10),
            'fecha_fin': date.today() + timedelta(days=15),
            'empleado': employee.id
        }
        serializer = RequestSerializer(data=data)
        assert not serializer.is_valid()

    def test_permission_anticipation(self, employee):
        """Verifica que permisos sin anticipación fallan."""
        data = {
            'tipo': 'permiso',
            'fecha_inicio': date.today(),
            'fecha_fin': date.today(),
            'empleado': employee.id
        }
        serializer = RequestSerializer(data=data)
        assert not serializer.is_valid()

    def test_permission_with_anticipation(self, employee):
        """Verifica que permisos con anticipación pasan."""
        data = {
            'tipo': 'permiso',
            'fecha_inicio': date.today() + timedelta(days=5),
            'fecha_fin': date.today() + timedelta(days=5),
            'empleado': employee.id
        }
        serializer = RequestSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_overlapping_requests(self, employee):
        """Verifica que solicitudes traslapadas fallan."""
        RequestSerializer().create({
            'tipo': 'vacacion',
            'fecha_inicio': date.today() + timedelta(days=10),
            'fecha_fin': date.today() + timedelta(days=15),
            'empleado': employee,
            'estatus': 'pendiente'
        })
        data = {
            'tipo': 'vacacion',
            'fecha_inicio': date.today() + timedelta(days=12),
            'fecha_fin': date.today() + timedelta(days=18),
            'empleado': employee.id
        }
        serializer = RequestSerializer(data=data)
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestAbsenceSerializer:
    """Tests para el serializer de inasistencias."""

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

    def test_valid_absence(self, employee):
        """Verifica que una inasistencia válida pasa."""
        data = {
            'empleado': employee.id,
            'fecha': date.today(),
            'tipo': 'injustificada',
            'motivo': 'No se presentó'
        }
        serializer = AbsenceSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_future_date_fails(self, employee):
        """Verifica que fechas futuras fallan."""
        data = {
            'empleado': employee.id,
            'fecha': date.today() + timedelta(days=1),
            'tipo': 'injustificada'
        }
        serializer = AbsenceSerializer(data=data)
        assert not serializer.is_valid()