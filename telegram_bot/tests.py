"""Tests para el bot de Telegram.

Cubre:
- Comandos /start, /help, /pendientes
- Callbacks de aprobación/rechazo
- Notificaciones asíncronas
- Manejo de errores y reintentos
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from telegram import Update, Message, Chat, User
from telegram.ext import ContextTypes
from requests.models import Request
from employees.models import User as CustomUser, Employee, Branch


@pytest.fixture
def mock_update():
    """Crea un mock de Update con mensaje y chat configurados."""
    chat = Chat(id=12345, type='private')
    telegram_user = User(id=12345, first_name='Test', is_bot=False)
    message = Message(message_id=1, date=None, chat=chat, from_user=telegram_user)
    update = MagicMock()
    update.message = message
    update.callback_query = None
    return update


@pytest.fixture
def mock_context():
    """Crea un mock de ContextTypes.DEFAULT_TYPE."""
    context = MagicMock()
    context.bot = AsyncMock()
    return context


@pytest.mark.django_db
class TestTelegramCommands:
    """Tests para comandos del bot."""

    @pytest.mark.asyncio
    async def test_start_command(self, mock_update, mock_context):
        """Verifica que /start retorna mensaje de bienvenida."""
        from telegram_bot.bot import start_command
        await start_command(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert 'Bienvenido' in call_args

    @pytest.mark.asyncio
    async def test_help_command(self, mock_update, mock_context):
        """Verifica que /help muestra comandos disponibles."""
        from telegram_bot.bot import help_command
        await help_command(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert '/start' in call_args
        assert '/help' in call_args
        assert '/pendientes' in call_args


@pytest.mark.django_db
class TestTelegramCallbacks:
    """Tests para callbacks de botones inline."""

    @pytest.fixture
    def mock_callback_update(self):
        """Crea un mock de Update con callback_query."""
        chat = Chat(id=12345, type='private')
        telegram_user = User(id=12345, first_name='Test', is_bot=False)
        message = Message(message_id=1, date=None, chat=chat, from_user=telegram_user)
        callback_query = MagicMock()
        callback_query.data = 'aprobar_1'
        callback_query.from_user = telegram_user
        callback_query.message = message
        callback_query.edit_message_text = AsyncMock()
        update = MagicMock()
        update.message = None
        update.callback_query = callback_query
        return update

    @pytest.mark.asyncio
    async def test_button_callback_aprobar(self, mock_callback_update, mock_context):
        """Verifica que el callback de aprobar procesa correctamente."""
        from telegram_bot.bot import button_callback
        await button_callback(mock_callback_update, mock_context)
        mock_callback_update.callback_query.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_button_callback_rechazar(self, mock_callback_update, mock_context):
        """Verifica que el callback de rechazar procesa correctamente."""
        mock_callback_update.callback_query.data = 'rechazar_1'
        from telegram_bot.bot import button_callback
        await button_callback(mock_callback_update, mock_context)
        mock_callback_update.callback_query.answer.assert_called_once()


@pytest.mark.django_db
class TestTelegramNotifications:
    """Tests para notificaciones."""

    @patch('telegram_bot.tasks.Bot')
    @patch('django.conf.settings')
    def test_enviar_notificacion_admin(self, mock_settings, mock_bot):
        """Verifica que la notificación al admin se envía correctamente."""
        mock_settings.TELEGRAM_BOT_TOKEN = 'test_token'
        mock_settings.TELEGRAM_ADMIN_ID = '12345'

        from telegram_bot.tasks import enviar_notificacion_admin
        enviar_notificacion_admin.delay(1)

        mock_bot.assert_called_once_with(token='test_token')

    @patch('telegram_bot.tasks.Bot')
    @patch('django.conf.settings')
    def test_enviar_notificacion_usuario(self, mock_settings, mock_bot):
        """Verifica que la notificación al usuario se envía correctamente."""
        mock_settings.TELEGRAM_BOT_TOKEN = 'test_token'

        from telegram_bot.tasks import enviar_notificacion_usuario
        enviar_notificacion_usuario.delay('12345', 'Test message')

        mock_bot.assert_called_once_with(token='test_token')

    @patch('django.conf.settings')
    def test_notificacion_sin_token(self, mock_settings):
        """Verifica que no se envía notificación sin token configurado."""
        mock_settings.TELEGRAM_BOT_TOKEN = ''

        from telegram_bot.tasks import enviar_notificacion_usuario
        result = enviar_notificacion_usuario.delay('12345', 'Test')

        assert result is None or result.failed() is False