import json
import os
from minecraft.mojang import convert_uuid


WHITELIST_PATH = os.environ.get("WHITELIST_PATH")


def whitelistf_add(username, uuid):
    """
    add the specified user to the whitelist
    are not already in the file.
    """
    uuid = convert_uuid(uuid)
    data = None
    with open(WHITELIST_PATH, "r") as file:
        data = json.load(file)

    if whitelistf_exists(username, uuid, data):
        return

    data += [{"name": username, "uuid": uuid}]

    with open(WHITELIST_PATH, "w") as file:
        json.dump(data, file, indent=4)


def whitelistf_rm(username, uuid):
    """
    remove the specified user from the whitelist
    if they are in the file.
    """
    uuid = convert_uuid(uuid)
    data = None
    with open(WHITELIST_PATH, "r") as file:
        data = json.load(file)

    if not whitelistf_exists(username, uuid, data):
        return

    data_new = [
        user for user in data if not (user["name"] == username and user["uuid"] == uuid)
    ]

    with open(WHITELIST_PATH, "w") as file:
        json.dump(data_new, file, indent=4)


def whitelistf_exists(username, uuid, data=None):
    """
    Check if the specified user is in the whitelist
        - if data is specified it is not loaded here
    """
    uuid = convert_uuid(uuid)
    if data is None:
        with open(WHITELIST_PATH, "r") as file:
            data = json.load(file)

    for user in data:
        if user["name"] == username and user["uuid"] == uuid:
            return True

    return False
