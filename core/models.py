from django.db import models


class Configuration(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'configurations'

    @classmethod
    def get(cls, key, default=None):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set(cls, key, value, description=''):
        obj, created = cls.objects.update_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )
        return obj


class NotificationLog(models.Model):
    TYPE_CHOICES = [
        ('telegram', 'Telegram'),
        ('email', 'Email'),
    ]
    STATUS_CHOICES = [
        ('sent', 'Enviado'),
        ('failed', 'Fallido'),
        ('pending', 'Pendiente'),
    ]

    tipo = models.CharField(max_length=20, choices=TYPE_CHOICES)
    destinatario = models.CharField(max_length=100)
    mensaje = models.TextField()
    estatus = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification_logs'
        ordering = ['-created_at']