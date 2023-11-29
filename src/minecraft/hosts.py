# helpers to deal with the hosts json file
import json

HOSTS = None
with open("./hosts.json") as file:
    HOSTS = json.load(file)


def get_host_details(key):
    for host in HOSTS:
        if key == host["hostname"] or key == host["name"]:
            return host
    return None


def host_get_value(hkey, key):
    host = get_host_details(hkey)
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


def hosts_to_addrs():
    return [f"{host['hostname']}:{host['port']}" for host in HOSTS]
