# server related methods, ie pinging server etc
import os
import shutil
import time
import socket
from PIL import Image
from html2image import Html2Image
from mcstatus import JavaServer
from data.hosts import (
    hosts_to_addrs,
    host_to_addr,
    hosts_get_active,
    host_get_details,
    HostNotRegistered,
)
from minecraft.skins import render_face
from minecraft.mojang import get_uuid

DEFAULT_PORT = 25565


def hostname_ensure_addr(addr):
    """
    ensure that the hostname is a somewhat proper address.

    if there isnt a port (ie a :) then assume its the default and append it
    """
    if len(addr.split(":")) == 2:
        return addr
    else:
        # assume default port
        return f"{addr}:{DEFAULT_PORT}"


def parse_host(addr):
    """
    Parse into just the hostname without port,
    unless the port is non standard in which case
    it is important to keep

    if for some reason there are multiple colons just take the hostname
    """

    # no port included so we assume its the default
    if not ":" in addr:
        return addr

    idx = addr.index(":")
    hostname = addr[:idx]
    port = addr[idx + 1 :]

    # multiple colons, give up and use what shld be hostname
    if ":" in port:
        return hostname

    # if default port return just hostname
    if port == str(DEFAULT_PORT):
        return hostname

    # seems the port is somewhat valid (not gonna check its int)
    return addr


def ping_old(addr):
    """
    since alpha / beta doesnt have the same protocol, we will just
    try to connect to the port, and assume if the port is open that
    the server is running

    # TODO figure out excatly what version the mcstatus package stops working
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        host, port = addr.split(":")
        s.connect((host, int(port)))
    except:
        return False
    return True


def get_server(addr):
    # TODO test if bedrock?
    server = JavaServer.lookup(hostname_ensure_addr(addr))
    return server


def server_ping(addr=None):
    host = None
    if addr is None:
        host = hosts_get_active()
        if "alpha" in host and host["alpha"]:
            return "Cannot ping apha server"
        addr = host_to_addr(host)

    server = get_server(addr)

    try:
        latency = server.ping()
    except TimeoutError:
        return "The server did not respond"
    return f"The server replied in {latency} ms"
