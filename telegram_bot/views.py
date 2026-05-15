"""Views y utilidades para integración del bot de Telegram con Django."""

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def webhook(request):
    """Endpoint para recibir webhooks de Telegram.

    Procesa las actualizaciones del bot cuando está configurado en modo webhook.
    """
    try:
        update = json.loads(request.body)
        logger.debug(f"Webhook recibido: {update}")
        return HttpResponse(status=200)
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        return HttpResponseBadRequest()


async def enviar_notificacion_usuario(chat_id: str, mensaje: str):
    """Envía notificación directa al usuario por Telegram.

    Args:
        chat_id: Chat ID de Telegram del usuario
        mensaje: Texto del mensaje a enviar
    """
    from telegram import Bot
    from django.conf import settings

    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("Token no configurado")
        return

    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=mensaje)