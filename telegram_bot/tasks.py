"""Tareas Celery para el bot de Telegram.

Contiene tareas asíncronas para:
- Notificar nuevas solicitudes al admin
- Enviar confirmaciones al empleado
- Reintentos automáticos en caso de fallo
"""

import logging
from celery import shared_task
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from django.conf import settings
from requests.models import Request

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_notificacion_admin(self, request_id: int):
    """Envía notificación al admin sobre una nueva solicitud.

    Args:
        request_id: ID de la solicitud recién creada

    Retries:
        3 intentos con delay de 60 segundos entre cada uno
    """
    try:
        request_obj = Request.objects.get(id=request_id)
    except Request.DoesNotExist:
        logger.error(f"Solicitud {request_id} no encontrada")
        return

    token = settings.TELEGRAM_BOT_TOKEN
    admin_id = settings.TELEGRAM_ADMIN_ID

    if not token or not admin_id:
        logger.warning("Token o Admin ID no configurados")
        return

    bot = Bot(token=token)

    keyboard = [
        [
            InlineKeyboardButton("✅ Aprobar", callback_data=f"aprobar_{request_id}"),
            InlineKeyboardButton("❌ Rechazar", callback_data=f"rechazar_{request_id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    mensaje = (
        f"📝 Nueva Solicitud #{request_id}\n\n"
        f"👤 Empleado: {request_obj.empleado.user.get_full_name()}\n"
        f"🔖 No. Empleado: {request_obj.empleado.employee_number}\n"
        f"📅 Tipo: {request_obj.get_tipo_display()}\n"
        f"📆 Inicio: {request_obj.fecha_inicio}\n"
        f"📆 Fin: {request_obj.fecha_fin}\n"
        f"📊 Días: {request_obj.dias_solicitados()}\n"
    )

    if request_obj.fuera_de_condiciones:
        mensaje += "\n⚠️ FUERA DE CONDICIONES / RIESGO DE ABANDONO\n"

    try:
        bot.send_message(chat_id=admin_id, text=mensaje, reply_markup=reply_markup)
        logger.info(f"Notificación enviada al admin {admin_id}")
    except Exception as e:
        logger.error(f"Error enviando notificación: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_notificacion_usuario(self, chat_id: str, mensaje: str):
    """Envía notificación al empleado sobre el estatus de su solicitud.

    Args:
        chat_id: Chat ID de Telegram del usuario
        mensaje: Texto del mensaje a enviar

    Retries:
        3 intentos con delay de 60 segundos entre cada uno
    """
    try:
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            logger.warning("Token no configurado")
            return

        bot = Bot(token=token)
        bot.send_message(chat_id=chat_id, text=mensaje)
        logger.info(f"Notificación enviada al usuario {chat_id}")
    except Exception as e:
        logger.error(f"Error enviando notificación al usuario: {e}")
        raise self.retry(exc=e)