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


class HostNotFound(Exception):
    def __init__(self, msg="The host was not found", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


HOSTS = None
with open("./data/hosts.json") as file:
    HOSTS = json.load(file)


# TODO refactor these cause they bother me
#       host_x functions should take a host json obj
#       and refer to one host
#
#       hosts_x functions should taake some other arg
#       and ook through the HOSTS var


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


def host_get_value(hkey, key, host=None):
    if host is None:
        host = host_get_details(hkey)

    if host is not None and key in host:
        return host[key]

    return None


def host_get_name(host):
    name = host_get_value("", "name", host=host)
    hostname = host_get_value("", "hostname", host=host)
    if name is None:
        name = hostname
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

    # default to first one if theres no bool
    return host[0]


def hosts_set_active(hostname):
    """
    Somewhat gross wrapper for if i need to do it by name
    """
    global active_server
    host_get_details(hostname)
    host_set_active(host_get_details(hostname))


def host_set_active(host):
    global active_server
    active_server = host


def hosts_get_active():
    return active_server


def host_get_by_ext(ext_name):
    for host in HOSTS:
        if "systemctl_ext" in host and host["systemctl_ext"] == ext_name:
            return host
    raise HostNotFound()


def hosts_get_all():
    return HOSTS


def hosts_get_integrated():
    # TODO better hosts get that only gets the ones u can send commands on
    return hosts_get_local()


def hosts_get_local():
    return [host for host in hosts_get_all() if "local" in host and host["local"]]


# load in the default server host
active_server = hosts_get_default()
