import time
import os
from html2image import Html2Image
from data.hosts import (
    hosts_to_addrs,
    host_to_addr,
    hosts_get_active,
    host_get_details,
    HostNotRegistered,
)
from minecraft.server import parse_host, get_server, ping_old

from render.helpers import merge_images, load_assets, unload_assets

DEFAULT_PORT = 25565


def servers_status(
    output_path="/tmp/", addrs=[host_to_addr(hosts_get_active())], options={}
):
    """
    render the statuses of the provided server addresses
    """
    if "all" in options and options["all"]:
        addrs = hosts_to_addrs()

    files = []
    for server in addrs:
        files += [server_status(output_path=output_path, addr=server, options=options)]

    path = f"/tmp/{time.time()}.png"
    merge_images(files, path)
    for file in files:
        os.remove(file)
    return path


def server_status(
    output_path="/tmp/", addr=host_to_addr(hosts_get_active()), options={}
):
    motd_html, favicon, players = [None] * 3
    addr = addr
    name = parse_host(addr)

    alpha = False
    # lookup name and check if server is alpha
    try:
        host = host_get_details(addr)
        if ("host" not in options or not options["host"]) and "name" in host:
            name = host["name"]
        if "alpha" in host and host["alpha"]:
            alpha = True
    except HostNotRegistered:
        pass

    # check actual server status
    try:
        srv = get_server(addr)
        status = srv.status()
        favicon = status.favicon
        players_online = status.players.online
        players_max = status.players.max
        players = '{}<span style="color: #4d4b4b">/</span>{}'.format(
            players_online, players_max
        )
        motd_html = status.motd.to_html().replace("\n", "<br>")
    except:
        players = ""
        motd_html = "<p><span style='color:red;'>Can't connect to server</span></p>"
        if alpha and ping_old(addr):
            motd_html = "<p>Connected to alpha server port<br><span style='color:orange;'><small>(port is open, but might not be a real server)</small></span></p>"

    if favicon is None:
        favicon = ""
    else:
        favicon = "style='background-image: url({})!important'".format(status.favicon)

    # load renderer
    hti = Html2Image(output_path=output_path, size=(512, 74))

    # load in formatting from files
    wrapping = None
    css = None
    with open("./public/motd.html") as file:
        wrapping = file.read()
    with open("./public/motd.css") as file:
        css = file.read()

    file = f"{addr}_motd.png"

    html = wrapping.format(favicon, name, players, motd_html)

    load_assets()
    hti.screenshot(html_str=html, css_str=css, save_as=file)
    unload_assets()

    return output_path + file
