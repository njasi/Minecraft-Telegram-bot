from telegram import Update
from telegram.ext import ContextTypes

HELP_STRING = '''<b>Help</b>
This is a simple bot used to check basic info about a minecraft server.

<b>Commands</b>
/online:
Check what players are online (obsfucated by some servers)
/status, /up:
Check server status.
/ping:
Measure the response time of the server.

If you're a chat admin there are some additional commands:
/serverstop:
Stop the server
/serverstart:
Start the server
/serverrestart:
Restart the server
/whitelistadd \<username\>
Add player to the whitelist
/whitelistrm \<username\>
Remove player from the whitelist
'''


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays help information, see the string above."""

    await update.effective_message.reply_html(HELP_STRING)
