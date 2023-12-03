import html
import json
import logging
import traceback
import os
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from handlers.start import start
from handlers.help import help
from handlers.whitelist import whitelistadd, whitelistrm
from handlers.ping import ping
from handlers.status import status
from handlers.online import online
from handlers.local import local
from handlers.activate import activate
from handlers.commands import commands
from handlers.messages import messages


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developers."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=os.environ.get("DEVELOPER_CHAT_ID"),
        text=message,
        parse_mode=ParseMode.HTML,
    )


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(os.environ.get("TOKEN")).build()

    # Register commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("whitelistadd", whitelistadd))
    application.add_handler(CommandHandler("whitelistrm", whitelistrm))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler(["status", "up"], status))
    application.add_handler(CommandHandler(["online", "tab"], online))
    application.add_handler(CommandHandler(["a", "activate", "active"], activate))
    application.add_handler(CommandHandler("local", local))

    # commands that dont fit the above get sent to the server console with the slash removed
    application.add_handler(MessageHandler(filters.COMMAND, commands))
    # remaining messages get sent to minecraft
    application.add_handler(MessageHandler(filters.TEXT, messages))

    # the error handler
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
