from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Employee, EmployeeAudit


@receiver(pre_save, sender=Employee)
def employee_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Employee.objects.get(pk=instance.pk)
            instance._old_status = old.status
            instance._old_saldo = old.saldo_vacaciones
        except Employee.DoesNotExist:
            pass


@receiver(post_save, sender=Employee)
def employee_post_save(sender, instance, created, **kwargs):
    user = getattr(instance, '_changed_by', None)
    if created:
        EmployeeAudit.objects.create(
            employee=instance,
            action='create',
            changed_by=user
        )
    else:
        if hasattr(instance, '_old_status') and instance._old_status != instance.status:
            EmployeeAudit.objects.create(
                employee=instance,
                action='status_change',
                field_changed='status',
                old_value=instance._old_status,
                new_value=instance.status,
                changed_by=user
            )
        if hasattr(instance, '_old_saldo') and instance._old_saldo != instance.saldo_vacaciones:
            EmployeeAudit.objects.create(
                employee=instance,
                action='balance_change',
                field_changed='saldo_vacaciones',
                old_value=str(instance._old_saldo),
                new_value=str(instance.saldo_vacaciones),
                changed_by=user
            )


def actualizar_saldo_aniversario():
    from datetime import date
    today = date.today()
    employees = Employee.objects.filter(status='activo')
    for emp in employees:
        if emp.fecha_ingreso.month == today.month and emp.fecha_ingreso.day == today.day:
            dias = emp.get_dias_vacaciones()
            emp.saldo_vacaciones += dias
            emp.save()