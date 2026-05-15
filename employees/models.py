"""Modelos para gestión de empleados, sucursales y auditoría."""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Modelo de usuario personalizado con roles y autenticación múltiple."""
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('user', 'Colaborador'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)
    api_key = models.CharField(max_length=64, blank=True, null=True, unique=True)

    class Meta:
        db_table = 'users'


class Branch(models.Model):
    """Representa una sucursal física de la empresa."""
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'branches'
        ordering = ['name']

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Perfil extendido del empleado con datos laborales y saldo de vacaciones."""
    STATUS_CHOICES = [
        ('activo', 'Activo'),
        ('baja', 'Baja'),
        ('suspendido', 'Suspendido'),
    ]
    CONTRACT_CHOICES = [
        ('laboral', 'Laboral'),
        ('mercantil', 'Mercantil'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    employee_number = models.CharField(max_length=20, unique=True)
    curp = models.CharField(max_length=18, blank=True)
    rfc = models.CharField(max_length=13, blank=True)
    tipo_contrato = models.CharField(max_length=20, choices=CONTRACT_CHOICES, default='laboral')
    fecha_ingreso = models.DateField()
    saldo_vacaciones = models.FloatField(default=0)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='employees')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'
        ordering = ['employee_number']

    def __str__(self):
        return f"{self.employee_number} - {self.user.get_full_name()}"

    def calcular_antiguedad(self):
        """Calcula la antigüedad en años desde la fecha de ingreso."""
        from datetime import date
        today = date.today()
        delta = today - self.fecha_ingreso
        return delta.days // 365

    def get_dias_vacaciones(self):
        """Retorna los días de vacaciones según antigüedad (LFT Art. 76)."""
        antiguedad = self.calcular_antiguedad()
        if antiguedad >= 20:
            return 20
        elif antiguedad >= 15:
            return 18
        elif antiguedad >= 10:
            return 16
        elif antiguedad >= 5:
            return 14
        elif antiguedad >= 4:
            return 12
        elif antiguedad >= 3:
            return 10
        elif antiguedad >= 2:
            return 8
        elif antiguedad >= 1:
            return 6
        return 0


class EmployeeAudit(models.Model):
    """Registro de auditoría para cambios en datos de empleados."""
    ACTION_CHOICES = [
        ('create', 'Creado'),
        ('update', 'Actualizado'),
        ('delete', 'Eliminado'),
        ('status_change', 'Cambio de estatus'),
        ('balance_change', 'Cambio de saldo'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='audits')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    field_changed = models.CharField(max_length=50, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'employee_audits'
        ordering = ['-created_at']