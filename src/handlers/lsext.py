from telegram import Update
from telegram.ext import ContextTypes
from minecraft.hosts import hosts_get_all, host_get_value, host_get_name


def make_ext_string(host):
    name = host_get_name(host)
    # TODO clean up the host methods
    ext = host_get_value("", "systemctl_ext", host=host)

    result = ""

    if ext is not None:
        result = f"<b>{name}</b>:\n\t{ext}\n"

    return result


async def lsext(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays start information, see the string above."""

    res = "<b>Local Hosts:</b>\n"
    hosts = hosts_get_all()
    for host in hosts:
        res += make_ext_string(host)

    if len(hosts) == 0:
        res = "There are no registered local hosts. Check the readme on how to add hosts to your hosts.json file"

    await update.effective_message.reply_html(res)
