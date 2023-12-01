from telegram import Update
from telegram.ext import ContextTypes

from minecraft.hosts import host_


USAGE_STRING = "/activate hostname"
async def activate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """sets a host as active"""
    # TODO

    await update.effective_message.reply_html("activating")
