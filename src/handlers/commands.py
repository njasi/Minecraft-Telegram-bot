from telegram import Update
from telegram.ext import ContextTypes

from minecraft.hosts import MissingSystemctlExt, NotLocalError
from minecraft.commands import send_command


async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """send an arbitrary command to the stdin of the active server"""

    try:
        send_command(update.message.text)
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

    # TODO get response from server stdout?

    await update.effective_message.reply_html("ran the command")
