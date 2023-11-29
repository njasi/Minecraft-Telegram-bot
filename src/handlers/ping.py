from telegram import Update
from telegram.ext import ContextTypes

from minecraft.server import server_ping


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays start information, see the string above."""

    response = (
        server_ping(addr=context.args[0]) if len(context.args) == 1 else server_ping()
    )

    await update.effective_message.reply_html(response)
