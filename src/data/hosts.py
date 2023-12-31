# helpers to deal with the hosts json file
import json
import os


class NotLocalError(Exception):
    def __init__(self, msg="Host not local", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class MissingSystemctlExt(Exception):
    def __init__(self, msg="Host does not have extname", *args, **kwargs):
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


# TODO refactor these cause they bother me
#       host_x functions should take a host json obj
#       and refer to one host
#
#       hosts_x functions should taake some other arg
#       and ook through the HOSTS var

# default host info to fill in gaps
DEFAULTS = None
HOSTS = None  # loaded in below
with open("./data/defaults.json") as file:
    DEFAULTS = json.load(file)


def host_ensure_defaults(host, defaults=DEFAULTS):
    """
    ensure that a given host has all the information that is required of it
    fill in missing informaion with defaults
    """

    for key in defaults:
        if key not in host:
            host[key] = defaults[key]
        elif host[key] is None:
            host[key] = defaults[key]
    return host


def hosts_ensure_defaults(hosts, defaults=DEFAULTS):
    return [host_ensure_defaults(host, defaults=defaults) for host in hosts]


# load in host config, and ensure defaults
with open("./data/hosts.json") as file:
    HOSTS = json.load(file)
    HOSTS = hosts_ensure_defaults(HOSTS)


def host_find(info):
    try:
        return host_get_by_addr(info)
    except HostNotFound:
        pass

    try:
        return hosts_get_by_ext(info)
    except HostNotFound:
        pass

    return None


def host_get_by_addr(addr, ext=None):
    """
    host get by address
    """
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
        if ext and host["extname"] == ext:
            return ext
        if (
            hostname == host["hostname"]
            and port == host["port"]
            or hostname == host["name"]
        ):
            return host
    raise HostNotFound()


def hosts_get_by_ext(extname):
    """
    Look through the hosts config json and
    find a host with a matching extname
    """
    for host in HOSTS:
        if host["extname"] == extname:
            return host
    raise HostNotFound()


def host_get_value(hkey, key, host=None):
    if host is None:
        host = host_find(hkey)

    if host is not None and key in host:
        return host[key]

    return None


def host_get_name(host):
    name = host_get_value("", "name", host=host)
    hostname = host_get_value("", "hostname", host=host)
    if name is None:
        name = hostname
    return name


def host_to_addr(host):
    return f"{host['hostname']}:{host['port']}"


def hosts_to_addrs():
    return [host_to_addr(host) for host in HOSTS]


def hosts_get_default():
    for host in HOSTS:
        if host["default"]:
            return host
    # return first one if none are set to default
    return host[0]


def hosts_set_active(hostname):
    """
    Somewhat gross wrapper for if i need to do it by name
    """
    global active_server
    host_find(hostname)
    host_set_active(host_find(hostname))


def host_set_active(host):
    """
    change the active host to the one given

    abstraction in case I want to store the active server in a different way later
    """
    global active_server
    active_server = host


def hosts_get_active():
    """
    get the active host

    abstraction in case I want to store the active server in a different way later
    """
    return active_server


def hosts_get_all():
    return HOSTS


def hosts_get_integrated():
    """
    Get the hosts that we caan actually send commands on,
    for now assume this is any host with systemctl_name set

    # TODO maybe add an integrated bool? idk if ur giving the bot systemctl access
    # it shld probably have minecraft cli access
    """
    return [
        host for host in hosts_get_all() if host["systemctl_name"] and host["local"]
    ]


def hosts_get_local():
    return [host for host in hosts_get_all() if host["local"]]


# load in the default server host
active_server = hosts_get_default()
