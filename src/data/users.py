import json
import random
import string
from minecraft.commands import send_code

USERS = None
JSON_PATH = "./data/users.json"


class UserNotFound(Exception):
    def __init__(self, msg="The telegram user was not found", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class UserNotMapped(Exception):
    def __init__(
        self, msg="Telegram user is not mapped to minecraft username", *args, **kwargs
    ):
        super().__init__(msg, *args, **kwargs)


class UserNotVerified(Exception):
    def __init__(self, msg="Minecraft username is not verified", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


def init_users():
    """
    very fancy function to "init" the "database"
    """
    users_load()


def users_load():
    """
    load in the user json
    """
    global USERS
    with open(JSON_PATH, "r+") as file:
        content = file.read()
        if content == "":
            USERS = {}
            users_update(USERS)
        USERS = json.loads(content)


def users_update(users):
    global USERS
    """
    dump object into the user json
    """
    USERS = users
    with open(JSON_PATH, "w") as file:
        json.dump(users, file, indent=4)


def users_find(telegram_id, id=None):
    """
    find a user directly from the json dict
    """
    for user in USERS:
        if id is not None and user[id] == telegram_id:
            # slightly cursed check so i dont have to rework this
            # to find by minecraft username
            return user
        elif user["telegram_id"] == telegram_id:
            return user
    raise UserNotFound()


def users_set(telegram_id, key, value):
    """
    update the value at key in a a user's object, and then update
    """
    users = USERS
    for user in users:
        if user["telegram_id"] == telegram_id:
            user[key] = value
            users_update(users)
            return

    raise UserNotFound()


def users_get(telegram_id, key, id=None):
    """
    get the value at key in a a user's object
    """
    user = users_find(telegram_id, id=id)
    return user[key]


def user_init(telegram_id):
    """
    generate default user with Nones
    """
    return {
        "telegram_id": telegram_id,
        "minecraft_username": None,
        "verification_code": None,
        "color": "blue",
    }


def user_add(telegram_id):
    """
    generate and a user to the users.json
    """
    newuser = user_init(telegram_id)
    users_update(USERS + [newuser])


def user_update(newuser):
    """
    update the entire user object with matching telegram id
    """
    users = USERS
    for user in users:
        if user["telegram_id"] == newuser["telegram_id"]:
            user = newuser
            users_update(users)
            return

    raise UserNotFound()


def users_telegram_to_minecraft(telegram_id):
    """
    map the telegram id to their minecraft username
    """
    vcode = users_get(telegram_id, "verification_code")
    if vcode == True:
        return users_get(telegram_id, "minecraft_username")

    raise UserNotVerified()


def users_minecraft_to_telegram(minecraft_username):
    """
    map the telegram id to their minecraft username
    """
    vcode = users_get(minecraft_username, "verification_code", id="minecraft_username")
    if vcode == True:
        return users_get(minecraft_username, "telegram_id", id="minecraft_username")

    raise UserNotVerified()


def users_send_verification(telegram_id, mc_username, code_length=6):
    """
    Send the verification code to all local servers
    (non alpha/beta, so no name faking)
    """

    code = "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(code_length)
    )

    users_set(telegram_id, "verification_code", code)
    users_set(telegram_id, "minecraft_username", mc_username)

    result = send_code(mc_username, code)
    # TODO, actually handle result, but i would need command results for it


def users_check_code(telegram_id, code):
    """
    Check if the code is correct and verify if it is

    return true if its a match, false if not
    """
    user = users_find(telegram_id)
    if user["verification_code"] is not None and code == user["verification_code"]:
        user["verification_code"] = True
        user_update(user)
        return True
    return False
