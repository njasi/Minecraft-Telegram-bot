from telegram import Update
from telegram.ext import ContextTypes

START_STRING = '''This is a simple bot used to check basic info about a minecraft server.

It can also be used to do simple server management if setup locally to the server'''


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays start information, see the string above."""

    await update.effective_message.reply_html(START_STRING)
