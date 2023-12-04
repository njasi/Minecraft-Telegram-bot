from telegram import Update
from telegram.ext import ContextTypes

from data.hosts import MissingSystemctlExt, NotLocalError
from minecraft.commands import send_user_message
from data.hosts import hosts_get_active


async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """send a telegram message into minecraft"""

    try:
        # TODO minecraft verification and map telegram user to minecraft user
        # TODO
        host = hosts_get_active()
        user = update.message.from_user.name
        send_user_message(user, update.message.text, host=host)
    except NotLocalError:
        await update.effective_message.reply_html(
            "The active server is not a local server"
        )
        return
    except MissingSystemctlExt:
        await update.effective_message.reply_html(
            "The server is missing systemctl_ext in the hosts.json file"
        )
        return

