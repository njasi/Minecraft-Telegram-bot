# TODO command for linking minecraft username to account, send code to the user in the minecraft servers
from telegram import Update
from telegram.ext import ContextTypes

from minecraft.commands import send_code
from data.users import users_send_verification, users_find, user_add, UserNotFound

USAGE = "USAGE: /link minecraft_username"


async def link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a verification code to the minecraft user in all the non alpha\beta servers"""

    if len(context.args) != 1:
        await update.effective_message.reply_html(USAGE)
        return

    # add user to json if they dont exist yet
    uid = update.message.from_user.id
    try:
        users_find(uid)
    except UserNotFound:
        user_add(uid)
    

    # send code and add it to ur verifiction
    name = context.args[0]
    users_send_verification(uid, name)

    await update.effective_message.reply_html(f"A verification code has been sent to {name}")
