from telegram import Update
from telegram.ext import ContextTypes

from minecraft.hosts import hosts_get_active


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """send an arbitrary command to the stdin of the active server"""
    # TODO

    await update.effective_message.reply_html("")
