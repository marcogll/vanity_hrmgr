import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler
from django.conf import settings
from requests.models import Request

logger = logging.getLogger(__name__)

APROBAR, RECHAZAR, COMENTARIO = range(3)

HANDLERS = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Bienvenido al Bot de HR Manager!\n\n"
        "Este bot te permite aprobar o rechazar solicitudes de permisos y vacaciones.\n\n"
        "Cuando haya una nueva solicitud, recibirás una notificación con los detalles."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Comandos disponibles:\n\n"
        "/start - Iniciar el bot\n"
        "/help - Mostrar esta ayuda\n"
        "/pendientes - Ver solicitudes pendientes"
    )

async def mostrar_solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE, request_obj: Request):
    keyboard = [
        [
            InlineKeyboardButton("✅ Aprobar", callback_data=f"aprobar_{request_obj.id}"),
            InlineKeyboardButton("❌ Rechazar", callback_data=f"rechazar_{request_obj.id}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    mensaje = (
        f"📝 Nueva Solicitud #{request_obj.id}\n\n"
        f"👤 Empleado: {request_obj.empleado.user.get_full_name()}\n"
        f"🔖 No. Empleado: {request_obj.empleado.employee_number}\n"
        f"📅 Tipo: {request_obj.get_tipo_display()}\n"
        f"📆 Inicio: {request_obj.fecha_inicio}\n"
        f"📆 Fin: {request_obj.fecha_fin}\n"
        f"📊 Días: {request_obj.dias_solicitados()}\n"
    )

    if request_obj.fuera_de_condiciones:
        mensaje += "\n⚠️ FUERA DE CONDICIONES / RIESGO DE ABANDONO\n"

    if update.callback_query:
        await update.callback_query.edit_message_text(mensaje, reply_markup=reply_markup)
    else:
        await update.message.reply_text(mensaje, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("aprobar_"):
        request_id = int(data.split("_")[1])
        await mostrar_formulario_accion(update, context, request_id, "aprobar")
    elif data.startswith("rechazar_"):
        request_id = int(data.split("_")[1])
        await mostrar_formulario_accion(update, context, request_id, "rechazar")

async def mostrar_formulario_accion(update: Update, context: ContextTypes.DEFAULT_TYPE, request_id: int, accion: str):
    try:
        request_obj = Request.objects.get(id=request_id)
    except Request.DoesNotExist:
        await update.callback_query.edit_message_text("❌ Solicitud no encontrada")
        return

    HANDLERS[update.callback_query.from_user.id] = {
        'request_id': request_id,
        'accion': accion
    }

    await update.callback_query.edit_message_text(
        f"Va a {accion.upper()} la solicitud #{request_id}.\n"
        f"¿Desea agregar un comentario? (responda con el comentario o envíe 'skip' para continuar)"
    )
    return COMENTARIO

async def comentario_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in HANDLERS:
        await update.message.reply_text("No hay solicitud en proceso")
        return

    handler = HANDLERS[user_id]
    request_id = handler['request_id']
    accion = handler['accion']
    comentario = update.message.text

    if comentario.lower() == 'skip':
        comentario = ""

    try:
        request_obj = Request.objects.get(id=request_id)
        request_obj.estatus = 'aprobado' if accion == 'aprobar' else 'rechazado'
        request_obj.comentario_admin = comentario
        request_obj.save()

        if request_obj.tipo == 'vacacion' and accion == 'aprobar':
            dias = request_obj.dias_solicitados()
            empleado = request_obj.empleado
            empleado.saldo_vacaciones -= dias
            empleado.save()

        estado = "✅ APROBADA" if accion == 'aprobar' else "❌ RECHAZADA"
        await update.message.reply_text(
            f"Solicitud #{request_id} {estado}\n"
            f"Empleado: {request_obj.empleado.user.get_full_name()}\n"
            f"Días: {request_obj.dias_solicitados()}"
        )

        if request_obj.empleado.user.telegram_chat_id:
            from telegram_bot.views import enviar_notificacion_usuario
            try:
                await enviar_notificacion_usuario(
                    request_obj.empleado.user.telegram_chat_id,
                    f"Tu solicitud de {request_obj.get_tipo_display()} ha sido {accion.upper()}da.\n"
                    f"Comentario: {comentario or 'Sin comentario'}"
                )
            except Exception as e:
                logger.error(f"Error enviando notificación: {e}")

        del HANDLERS[user_id]

    except Request.DoesNotExist:
        await update.message.reply_text("❌ Solicitud no encontrada")

async def pendientes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pendientes = Request.objects.filter(estatus='pendiente')[:10]
    if not pendientes:
        await update.message.reply_text("No hay solicitudes pendientes")
        return

    for req in pendientes:
        await mostrar_solicitud(update, context, req)


def setup_bot():
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN no configurado")
        return None

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("pendientes", pendientes_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    return application


async def notificar_nueva_solicitud(request_id: int):
    from django.conf import settings
    from telegram import Bot

    try:
        request_obj = Request.objects.get(id=request_id)
    except Request.DoesNotExist:
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
        await bot.send_message(chat_id=admin_id, text=mensaje, reply_markup=reply_markup)
        logger.info(f"Notificación enviada al admin {admin_id}")
    except Exception as e:
        logger.error(f"Error enviando notificación: {e}")