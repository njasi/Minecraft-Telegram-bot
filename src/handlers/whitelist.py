from telegram import Update
from telegram.ext import ContextTypes
from minecraft.skins import render_url
from minecraft.mojang import get_uuid
from data.whitelist import (
    whitelistf_add,
    whitelistf_rm,
    whitelistf_exists,
    WhitelistError,
)
from minecraft.commands import send_whitelist_reload

USAGE_STRING = """USAGE:\t/whitelist{} username [extname]\n\n(optional host ext name not implemented yet cause im lazy)"""


async def whitelistadd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays start information, see the string above."""
    if not len(context.args) == 1:
        await update.effective_message.reply_html(USAGE_STRING.format("add"))
        return

    name = context.args[0]
    uuid = get_uuid(name)
    if not uuid:
        await update.effective_message.reply_html(
            "This minecraft account does not seem to exist..."
        )
        return

    try:
        if whitelistf_exists(name, uuid):
            await update.effective_message.reply_html(
                "This minecraft account is already whitelisted."
            )
            return

        message = await update.effective_message.reply_photo(
            caption=f"Whitelisting {name}", photo=render_url(uuid)
        )

        whitelistf_add(name, uuid)

        await context.bot.edit_message_caption(
            chat_id=update.effective_chat.id,
            message_id=message.message_id,
            caption=f"Successfully whitelisted {name}. This should take effect in a few minutes.",
        )

        # TODO properly handle this
        try:
            send_whitelist_reload()
        except:
            pass

    except WhitelistError:
        await update.effective_message.reply_html(
            text=f"This server does not have a whitelist file configured",
        )


async def whitelistrm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """remove players from the whitelist"""
    if not len(context.args) == 1:
        await update.effective_message.reply_html(USAGE_STRING.format("rm"))
        return

    name = context.args[0]
    uuid = get_uuid(name)

    if not uuid:
        await update.effective_message.reply_html(
            "This minecraft account does not seem to exist..."
        )
        return
    try:
        if not whitelistf_exists(name, uuid):
            await update.effective_message.reply_html(
                "This minecraft username was not on the whitelist."
            )
            return

        message = await update.effective_message.reply_html(
            f"Removing {name} from the whitelist"
        )

        whitelistf_rm(name, uuid)

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message.message_id,
            text=f"Successfully removed {name} from the whitelist. This should take effect in a few minutes.",
        )

        # TODO properly handle this
        try:
            send_whitelist_reload()
        except:
            pass

    except WhitelistError:
        await update.effective_message.reply_html(
            text=f"This server does not have a whitelist file configured",
        )
