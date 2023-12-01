import os
from telegram import Update
from telegram.ext import ContextTypes
from minecraft.server import server_online


async def online(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays server status, and motd render"""

    photo = (
        server_online(addr=context.args[0]) if len(context.args) == 1 else server_online()
    )

    await update.effective_message.reply_photo(photo=photo)
    os.remove(photo)
