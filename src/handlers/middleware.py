"""
Middleware function generators to control access / control flow for handlers
"""
import json
import os
from random import choice
from time import sleep
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

MINECRAFT_CHAT_ID = os.getenv("MINECRAFT_CHAT_ID")
CONFIG_ADMINS = []
MOCK_STICKERS = []


def load_env_json():
    global CONFIG_ADMINS, MOCK_STICKERS
    try:
        CONFIG_ADMINS = json.loads(os.getenv("ADMINS"))
    except:
        print("Error loading admin config")
    try:
        MOCK_STICKERS = json.loads(os.getenv("MOCK_STICKERS"))
    except:
        print("Error loading mocking stickers config")


load_env_json()


async def update_from_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Check if the update is from an admin either:
        - defined in the env file
        - chat admin in the Minecraft chat on telegram
    """
    user_id = update.message.from_user.id
    try:
        # check if user is one of the predefined admins in the config
        if user_id in CONFIG_ADMINS:
            return True

        # or if they are one of the admins of the minecraft telegram chat
        # TODO add config & an option to turn this off idk
        admins = await context.bot.get_chat_administrators(MINECRAFT_CHAT_ID)
        return update.message.from_user.id in [admin.user.id for admin in admins]
    except:
        return False


async def mock_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    send sticker / message to mock non admin user
    """
    message = None
    if len(MOCK_STICKERS) == 0:
        message = await update.effective_message.reply_html(
            "Only an admin can do this.",
            reply_to_message_id=update.effective_chat.id,
        )
    else:
        message = await context.bot.send_sticker(choice(MOCK_STICKERS))

    sleep(5)

    await context.bot.delete_message(
        chat_id=update.message.chat_id, message_id=update.message.id
    )
    await context.bot.delete_message(chat_id=message.chat_id, message_id=message.id)


def is_admin(handler, mock=True):
    """
    Function generator as it doesnt look like the telegram bot api supports
    middleware of any kind. Kinda weird tbh.
    """

    async def is_admin_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
        is_admin = await update_from_admin(update, context)
        if is_admin:
            return await handler(update, context)
        elif mock:
            try:
                mock_user(update, context)
            except:
                pass

    return is_admin_middleware


def is_chat(handler, chat_id, handler_wrong=None):
    """
    Will only preform the handler in the chat specified by <chat_id>.

    if its the wrong chat, use the handler_wrong instead if its specified
    """

    async def is_chat_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id == chat_id:
            return await handler(update, context)
        else:
            if handler_wrong is not None:
                return await handler_wrong(update, context)

    return is_chat_middleware
