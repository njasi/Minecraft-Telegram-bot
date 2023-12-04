from telegram import Update
from telegram.ext import ContextTypes
from data.hosts import hosts_get_local, host_get_value, host_get_name, host_to_addr


def make_ext_string(host):
    name = host_get_name(host)
    # TODO clean up the host methods
    ext = host_get_value("", "systemctl_ext", host=host)
    wp = host_get_value("", "whitelist_path", host=host)
    wp = "enabled" if wp else "disabled"
    addr = host_to_addr(host)

    result = ""

    if ext is not None:
        result = f"<u>{name}</u>: \n<pre>extname:\t{ext}\naddress:\t{addr}\nwhitelist integration:\t{wp}</pre>\n\n"

    return result


async def local(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lists the local servers."""

    res = "<b>Local Minecraft Servers:</b>\n\n"
    hosts = hosts_get_local()
    for host in hosts:
        res += make_ext_string(host)

    if len(hosts) == 0:
        res = "There are no registered local hosts. Check the readme on how to add hosts to your hosts.json file"

    await update.effective_message.reply_html(res)
