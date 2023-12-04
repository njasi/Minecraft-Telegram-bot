from telegram import Update
from telegram.ext import ContextTypes

from data.hosts import MissingSystemctlExt, NotLocalError
from minecraft.commands import broadcast_user_message
from data.hosts import hosts_get_active


async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """send a telegram message into minecraft"""

    try:
        # TODO map telegram user to minecraft user
        user = update.message.from_user.name

        # sends user message to all integrated hosts
        broadcast_user_message(user, update.message.text)

    # TODO refactor this now that it sends to all
    except NotLocalError:
        await update.effective_message.reply_html(
            "The active server is not a local server"
        )
        return
    except MissingSystemctlExt:
        await update.effective_message.reply_html(
            "A local server is missing systemctl_ext in the hosts.json file"
        )
        return
