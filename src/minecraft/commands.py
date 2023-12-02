from minecraft.hosts import hosts_get_active, NotLocalError, MissingSystemctlExt


SERVER_PATH = "/srv/minecraft/{}/systemd.stdin"


def send_whitelist_reload():
    send_command("whitelist reload")


def send_tellraw(user, message, color="blue"):
    command = '/tellraw @a [\{"text":"<", "color":"white"\},\{"text":"{}", "color":"{}"\},\{"text":"> {}", "color":"white"\}]'.format(
        user, color, message
    )
    send_command(command)


def send_command(command):
    if command.index("/") == 0:
        # chop out any slashes that are directly from the bot
        command = command[1:]

    active = hosts_get_active()

    if not active["local"]:
        raise NotLocalError()
    if "systemctl_ext" not in active:
        raise MissingSystemctlExt()

    # TODO test this, change to echo if needed
    with open(SERVER_PATH.format(active["systemctl_ext"]), "w") as file:
        file.write(command + "\n")
        file.flush()
