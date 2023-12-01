# helpers to deal with the hosts json file
import json
import os


class NotLocalError(Exception):
    def __init__(self, msg="Host not local", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class MissingSystemctlExt(Exception):
    def __init__(self, msg="Host does not have systemctl_ext", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class MissingSystemctlName(Exception):
    def __init__(self, msg="Host does not have systemctl_name", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class HostNotRegistered(Exception):
    def __init__(self, msg="The host is not registered", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


HOSTS = None
with open("./hosts.json") as file:
    HOSTS = json.load(file)


def host_get_details(addr, ext=None):
    hostname = addr
    port = 25565
    parts = addr.split(":")
    if len(parts) == 2:
        hostname, port = parts
        try:
            port = int(port)
        except:
            pass

    for host in HOSTS:
        if ext and host["systemctl_ext"] == ext:
            return ext
        if (
            hostname == host["hostname"]
            and port == host["port"]
            or hostname == host["name"]
        ):
            return host
    raise HostNotRegistered()


def host_get_value(hkey, key):
    host = host_get_details(hkey)
    if host is not None and key in host:
        return host[key]
    return None


def host_get_pretty_name(hkey):
    name = host_get_value(hkey, "name")
    if name is None:
        return hkey
    return name


def host_get_port(hkey):
    return host_get_value(hkey, "port")


def host_to_addr(host):
    return f"{host['hostname']}:{host['port']}"


def hosts_to_addrs():
    return [host_to_addr(host) for host in HOSTS]


def hosts_get_default():
    for host in HOSTS:
        if "default" in host and host["default"]:
            return host
    return None


def hosts_set_active(hostname=None, ext=None):
    global active_server
    active_server = host_get_details(hostname, ext)
    print(active_server, hostname)


def hosts_get_active():
    return active_server


# load in the default server host
active_server = hosts_get_default()
