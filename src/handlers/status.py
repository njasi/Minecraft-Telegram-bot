import os
from telegram import Update
from telegram.ext import ContextTypes
from render.status import servers_status

# telegram is annoying and consolidates -- into "—" on some clients
DOUBLE_DASH = "—"


def removeall(lst, target):
    while lst.count(target):
        lst.remove(target)
    return lst


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays server status, and motd render"""

    options = {}
    if (
        f"{DOUBLE_DASH}hostname" in context.args
        or "-h" in context.args
        or "--hostname" in context.args
    ):
        options["host"] = True
        context.args = removeall(context.args, f"{DOUBLE_DASH}hostname")
        context.args = removeall(context.args, "--hostname")
        context.args = removeall(context.args, "-h")

    if (
        f"{DOUBLE_DASH}all" in context.args
        or "--a" in context.args
        or "-a" in context.args
    ):
        options["all"] = True
        context.args = []

    photo = (
        servers_status(addrs=context.args, options=options)
        if len(context.args) > 0
        else servers_status(options=options)
    )
    await update.effective_message.reply_photo(photo=photo)
    os.remove(photo)
