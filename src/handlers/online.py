import os
from telegram import Update
from telegram.ext import ContextTypes
from render.online import render_online


async def online(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays server status, and motd render"""

    photo = (
        render_online(addr=context.args[0]) if len(context.args) == 1 else render_online()
    )

    await update.effective_message.reply_photo(photo=photo)
    os.remove(photo)
