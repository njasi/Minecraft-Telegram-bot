import os
from telegram import Update
from telegram.ext import ContextTypes

from data.hosts import MissingSystemctlExt, NotLocalError
from minecraft.commands import broadcast_user_message
from data.users import (
    users_find,
    user_add,
    users_telegram_to_minecraft,
    users_check_code,
    UserNotVerified,
    UserNotFound,
)

MC_CHAT_ID = int(os.environ.get("MINECRAFT_CHAT_ID"))

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """send a telegram message into minecraft"""

    try:
        user = users_find(update.message.from_user.id)
        mcu = users_telegram_to_minecraft(update.message.from_user.id)
        if not update.effective_chat.id == MC_CHAT_ID:
            return # only forward messages that are in the minecraft chat
        # sends user message to all integrated hosts
        broadcast_user_message(mcu, update.message, color=user["color"])
    except UserNotVerified:
        # would be more prudent to verify in a command or reply but we dont need to
        if users_check_code(update.message.from_user.id, update.message.text):
            await update.effective_message.reply_html(
                "Your minecraft username has been verified.\n\nNow when you send a normal message to me or to the chat it will be sent to all the active dabney minecraft servers in chat as your username."
            )
    except UserNotFound:
        user_add(update.message.from_user.id)

    except NotLocalError:
        await update.effective_message.reply_html(
            "The active server is not a local server"
        )
        return
    except MissingSystemctlExt:
        await update.effective_message.reply_html(
            "A local server is missing extname in the hosts.json file"
        )
        return
