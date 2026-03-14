import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.bot.handler import process_message
from app.config import settings

logger = logging.getLogger(__name__)

WELCOME_MESSAGE = (
    "⚽ Welcome to FootballBot!\n\n"
    "I help you find and organize soccer matches. You can:\n\n"
    "• Tell me you want to **create a game** and I'll set it up\n"
    "• Ask me to **find games** near you\n"
    "• **Join a game** from the list\n\n"
    "Just chat with me naturally — e.g. "
    '"I want to play soccer tonight" or '
    '"I\'m organizing a 5v5 game tomorrow at Central Park"'
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    text = update.message.text

    try:
        response_text = await process_message(
            platform="telegram",
            user_id=str(user.id),
            username=user.username or "unknown",
            name=user.first_name or "unknown",
            text=text,
        )

        if len(response_text) > 4096:
            for i in range(0, len(response_text), 4096):
                await update.message.reply_text(response_text[i : i + 4096])
        else:
            await update.message.reply_text(response_text)

    except Exception:
        logger.exception("Error processing message")
        await update.message.reply_text(
            "Sorry, something went wrong. Please try again."
        )


def create_telegram_application() -> Application:
    app = Application.builder().token(settings.telegram_token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app
