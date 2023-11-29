# these commands are all abt the same, so theyre in this file together

from telegram import Update
from telegram.ext import ContextTypes
import os


# TODO link to active server
SERVICE_NAME = os.environ.get("TOKEN")

def push_systemctl_command(command):
    # make sure you've given your user sudo perms for at least systemctl
    # id reccomend making it specifically just /bin/systemctl
    os.system(f"sudo systemctl {command} {SERVICE_NAME}")

async def stopserver(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """stops the server using systemctl"""

    push_systemctl_command("stop")

    await update.effective_message.reply_html()


async def startserver(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """starts the server using systemctl"""

    push_systemctl_command("start")

    await update.effective_message.reply_html()


async def restartserver(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """starts the server using systemctl"""

    push_systemctl_command("restart")

    await update.effective_message.reply_html()
