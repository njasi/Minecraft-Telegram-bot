from telegram import Update
from telegram.ext import ContextTypes
from data.hosts import (
    host_set_active,
    hosts_get_by_ext,
    hosts_get_active,
    host_get_name,
    host_to_addr,
    HostNotFound,
)


USAGE_STRING = "/activate [hostname]"


async def activate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """sets a host as active, or sends the active host"""
    # TODO

    if len(context.args) > 1:
        await update.effective_message.reply_html(USAGE_STRING)
        return

    if len(context.args) == 0:
        host = hosts_get_active()
        name = host_get_name(host)
        addr = host_to_addr(host)
        await update.effective_message.reply_html(
            f"The active host is:\n\n<b>{name}</b>\n{addr}"
        )
        return

    ext_name = context.args[0]
    try:
        host = hosts_get_by_ext(ext_name)
        host_set_active(host)
        addr = host_to_addr(host)
        await update.effective_message.reply_html(
            f"The active host is now:\n\n<b>{host_get_name(host)}</b>\n{addr}."
        )
    except HostNotFound:
        await update.effective_message.reply_html(
            f'Could not find a server with the short name "{ext_name}".'
        )
