from telegram import Update
from telegram.ext import ContextTypes

from minecraft.hosts import MissingSystemctlExt, NotLocalError
from minecraft.commands import send_tellraw


async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """send a telegram message into minecraft"""

    try:
        # TODO minecraft verification and map telegram user to minecraft user
        user = update.message.from_user.name
        # TODO make a send tell varient for the older servers
        send_tellraw(user, update.message.text)
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
