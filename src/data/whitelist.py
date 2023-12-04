import json
from minecraft.mojang import convert_uuid
from data.hosts import hosts_get_active, hosts_get_all


class WhitelistError(Exception):
    def __init__(self, msg="No whitelist path for the active server", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


def get_active_whitelist():
    active = hosts_get_active()
    if active is not None and "whitelist_path" in active:
        return active["whitelist_path"]
    raise WhitelistError()


def whitelistable():
    """
    get list of all hosts that have whitelist_path which is a strring
    """
    [
        host
        for host in hosts_get_all()
        if "whitelist_path" in host and isinstance(host["whitelist_path"], str)
    ]


def whitelistf_add(username, uuid):
    """
    add the specified user to the whitelist
    are not already in the file.
    """
    whitelist_path = get_active_whitelist()

    uuid = convert_uuid(uuid)
    data = None
    with open(whitelist_path, "r") as file:
        data = json.load(file)

    if whitelistf_exists(username, uuid, data):
        return

    data += [{"name": username, "uuid": uuid}]

    with open(whitelist_path, "w") as file:
        json.dump(data, file, indent=4)


def whitelistf_rm(username, uuid):
    """
    remove the specified user from the whitelist
    if they are in the file.
    """
    whitelist_path = get_active_whitelist()
    uuid = convert_uuid(uuid)
    data = None
    with open(whitelist_path, "r") as file:
        data = json.load(file)

    if not whitelistf_exists(username, uuid, data):
        return

    data_new = [
        user for user in data if not (user["name"] == username and user["uuid"] == uuid)
    ]

    with open(whitelist_path, "w") as file:
        json.dump(data_new, file, indent=4)


def whitelistf_exists(username, uuid, data=None):
    """
    Check if the specified user is in the whitelist
        - if data is specified it is not loaded here
    """
    whitelist_path = get_active_whitelist()
    uuid = convert_uuid(uuid)
    if data is None:
        with open(whitelist_path, "r") as file:
            data = json.load(file)

    for user in data:
        if user["name"] == username and user["uuid"] == uuid:
            return True

    return False


def whitelistf_all(username, uuid, func=whitelistf_add):
    hw = whitelistable()
    stats = []
    for h in hw:
        func(username, uuid)
