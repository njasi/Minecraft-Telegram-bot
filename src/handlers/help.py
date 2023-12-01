from telegram import Update
from telegram.ext import ContextTypes

HELP_STRING = """<b>Help</b>
This is a simple bot used to check basic info about a minecraft server.

<b>Commands:</b>
/status [hostname...] -a,--all -h,--hostname
    Check server(s) status, renders motd like in the minecraft launcher.
    -a, --all: show all of the hosts in your hosts file.
    -h, --hostname: show hostnames instead of pretty names.
/online [hostname]:
    Check what players are online (obsfucated by some servers)
/ping [hostname]:
Measure the response time of the server.

<b>If you're a chat admin there are some additional commands:</b>

/activate extname
    Select the active server by it's extname
/serverstop [extname]:
    Stop the server
/serverstart [extname]:
    Start the server, defaults to active server
/serverrestart [extname]:
    Restart the server, defaults to active server
/whitelistadd username [extname]
    Add player to the whitelist of the active server
/whitelistrm username [extname]
    Remove player from the whitelist of the active server
/lsext:
    list server extnames
"""


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays help information, see the string above."""

    await update.effective_message.reply_html(HELP_STRING)
