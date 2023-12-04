from data.hosts import hosts_get_active, NotLocalError, MissingSystemctlExt
import json


SERVER_PATH = "/srv/minecraft/{}/systemd.stdin"


def send_whitelist_reload(host=None):
    send_command("whitelist reload", host=host)


def send_verificaion_code(user, code, host=None):
    send_command(f"tell {user} Your verification code is {code}", host=host)


def ensure_string(message):
    try:
        return json.dumps(message)
    except:
        return message


def tellraw_to_tell_string(message):
    try:
        data = json.loads(message)

        if isinstance(data, list):
            result = ""
            for item in data:
                try:
                    result += item["text"]
                except:
                    pass
            return result
        else:
            return data["text"]
    except:

        return message


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
    #


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


def send_user_message(user, message, color="blue", host=None):
    message = '[{{"text":"<", "color":"white"}},{{"text":"{}", "color":"{}"}},{{"text":"> {}", "color":"white"}}]'.format(
        user, color, message
    )
    send_tell_general(message, host=host)


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

    # TODO test this, change to echo if needed
    with open(SERVER_PATH.format(active["systemctl_ext"]), "w") as file:
        file.write(command + "\n")
        file.flush()
