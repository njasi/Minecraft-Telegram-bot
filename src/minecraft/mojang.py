# helpers for pinging the mojang servers

from mojang import API
from uuid import UUID

# Create a Public API instance
api = API()


def get_uuid(name):
    uuid = api.get_uuid(name)
    if not uuid:
        return False
    return uuid


def convert_uuid(uuid):
    """
    change the uuid returned by the api into the same
    form stored in the whitelist json
    """

    return UUID(uuid).__str__()
