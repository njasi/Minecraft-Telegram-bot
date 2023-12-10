from telegram import Update
from telegram.ext import ContextTypes

from data.hosts import MissingSystemctlExt, NotLocalError
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
            "The server is missing extname in the hosts.json file"
        )
        return
    except FileNotFoundError:
        await update.effective_message.reply_html(
            "Could not find the systemd.stdin file, check your configuration."
        )
        return
    except Exception as e:
        await update.effective_message.reply_html(
            "There was an unknown error while executing your command."
        )
        raise e

    # TODO get response from server stdout?
    # make it check journalctl? or can systemd output two places

    await update.effective_message.reply_html("ran the command")
