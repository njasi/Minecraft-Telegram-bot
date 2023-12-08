from data.hosts import (
    hosts_get_active,
    NotLocalError,
    MissingSystemctlExt,
    hosts_get_integrated,
    host_to_addr,
)
import json
import os
from telegram import Message, MessageEntity

# omitting white
TELLRAW_COLORS = [
    "black",
    "dark_blue",
    "dark_green",
    "dark_aqua",
    "dark_red",
    "dark_purple",
    "dark_gray",
    "gold",
    "gray",
    "blue",
    "green",
    "aqua",
    "red",
    "light_purple",
    "yellow",
]


SERVER_PATH = "/srv/minecraft/{}/systemd.stdin"

ENTITY_TO_PROPERTY = {
    MessageEntity.BOLD: "bold",
    MessageEntity.ITALIC: "italic",
    MessageEntity.STRIKETHROUGH: "strikethrough",
    MessageEntity.UNDERLINE: "underline",
    MessageEntity.SPOILER: "obfuscated",
}


def telegram_to_tellraw_array(message: Message):
    # NOTE: it doesnt look like thie entities can overlap but i dont
    # trust the api or this package
    text = message.text

    changes = {}

    def add_change(i, type, pos):
        if i not in changes:
            changes[i] = []
        changes[i].append({"type": ENTITY_TO_PROPERTY[type], "pos": pos})

    for ent in message.entities:
        try:
            add_change(ent.offset, ent.type, "start")
            add_change(ent.offset + ent.length, ent.type, "end")
        except KeyError:
            pass

    tellraw_json = []
    current_text = ""
    current_entities = {}

    def add_tellraw_json():
        nonlocal current_text
        tellraw_json.append({"text": current_text, **current_entities})
        current_text = ""

    for i, char in enumerate(text):
        if i in changes:
            # if there are changes we need to make a new message obj
            # so clear the old one
            add_tellraw_json()
            # modify the current ent var
            for change in changes[i]:
                if change["pos"] == "end":
                    del current_entities[change["type"]]
                elif change["pos"] == "start":
                    current_entities[change["type"]] = True
        current_text += char
    add_tellraw_json()

    tellraw_spoiler = []
    # make both content and value, for different version support
    spoiler_component = {
        "obfuscated": True,
        "text": "",
        "hoverEvent": {"action": "show_text", "value": "", "content": ""},
    }
    spoiler_edited = False
    # pass through to find any with obsfucation set to true
    # join adjecent ones and remove formatting
    for component in tellraw_json:
        if "obfuscated" in component:
            spoiler_edited = True
            spoiler_component["text"] += component["text"]
            spoiler_component["hoverEvent"]["value"] += component["text"]
            spoiler_component["hoverEvent"]["content"] += component["text"]

        else:
            if spoiler_edited:
                spoiler_edited = False
                tellraw_spoiler.append(spoiler_component)
                spoiler_component = {
                    "obfuscated": True,
                    "text": "",
                    "hoverEvent": {"action": "show_text", "value": "", "content": ""},
                }
            tellraw_spoiler.append(component)

    # add the last one if we happen to end on spoiler
    if spoiler_edited:
        tellraw_spoiler.append(spoiler_component)

    return tellraw_spoiler


def send_whitelist_reload(host=None):
    send_command("whitelist reload", host=host)


def ensure_string(message):
    try:
        return json.dumps(message)
    except:
        return message


ERROR_TELLRAW_JSON = "Invalid tellraw json string: {}"


def tellraw_to_tell_string(message):
    """
    "Reasonable" conversion from tellraw message to just text
    for /tell or /say
    """
    try:
        data = json.loads(message)
        if isinstance(data, list):
            return "".join([item["text"] for item in data])
        elif isinstance(data, str):
            return data
        return data["text"]
    except KeyError:
        return ERROR_TELLRAW_JSON.format("missing text key")
    except json.JSONDecodeError:
        return ERROR_TELLRAW_JSON.format("error decoding")


def send_tell(message, target="@a", host=None, command="tell"):
    send_command(f"{command} {target} {message}", host=host)


def send_tell_general(message, target="@a", host=None):
    """
    expect a tellraw type string message with json

    message: (string | any) either a plain string, json string, or json object
    """
    # TODO make this check the server version for if it has tellraw
    # and then just use tell instead, or maybe say
    has_tellraw = True
    use_say = False

    if "alpha" in host and host["alpha"]:
        use_say = True

    # if version < "1.4.2":
    #     1.4.2 is the first to have @a
    #     use_say = True

    # if version >= "1.7.2":
    #     1.7.2 is the first version to have tellraw

    if use_say:
        # - exclude target in say
        # - for versions that dont have @a yet
        # - generally tell is better as it excludes the "[server]" part
        message = tellraw_to_tell_string(message)
        send_tell(message, target="", host=host, command="say")
    elif has_tellraw:
        send_tell(message, target=target, host=host, command="tellraw")
    else:
        message = tellraw_to_tell_string(message)
        send_tell(message, target=target, host=host)


def send_user_message(user, contents, color="blue", host=None):
    message = [
        {"text": "<", "color": "white"},
        {"text": f"{user}", "color": f"{color}"},
        {"text": "> ", "color": "white"},
        *contents,
    ]
    send_tell_general(json.dumps(message), host=host)


def broadcast_user_message(user, message: Message, color="blue"):
    contents = telegram_to_tellraw_array(message)
    for host in hosts_get_integrated():
        send_user_message(user, contents, host=host, color=color)


def send_code(mc_username, code):
    """
    send a message to all non alpha/beta servers to
    check if the telegram user really has this username
    not really needed but idk
    """

    # NOTE: 1.15 added the copy action, there are no errors
    #       if this is sent to an older version
    message_json = [
        {"text": "Your verification code is "},
        {
            "text": f"{code}",
            "color": "green",
            "clickEvent": {"action": "copy_to_clipboard", "value": f"{code}"},
        },
    ]
    message = json.dumps(message_json)
    for host in hosts_get_integrated():
        # TODO actual version checking
        if host["alpha"] == True:
            continue

        # servers that would use the say command wont be used
        # for verification so just choose a target
        send_tell_general(
            message,
            target=mc_username,
            host=host,
        )


def send_command(command, host=None):
    if len(command) <= 0:
        return

    # load in active host if we dont pass one
    active = host
    if host is None:
        active = hosts_get_active()

    if command[0] == "/":
        # chop out any slashes that are directly from the bot
        command = command[1:]

    # if its not local or setup raise error
    if not active["local"]:
        raise NotLocalError()
    if "systemctl_ext" not in active:
        raise MissingSystemctlExt()

    if os.getenv("ENV") == "develop":
        print(f"EXECUTE COMMAND:\n\thost:\t{host_to_addr(active)}\n\tcmd:\t{command}")
        return

    # TODO test this, change to echo if needed
    with open(SERVER_PATH.format(active["systemctl_ext"]), "w") as file:
        file.write(command + "\n")
        file.flush()
