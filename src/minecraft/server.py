# server related methods, ie pinging server etc
import os
import shutil
import time
import socket
from PIL import Image
from html2image import Html2Image
from mcstatus import JavaServer
from minecraft.hosts import (
    hosts_to_addrs,
    host_to_addr,
    hosts_get_active,
    host_get_details,
    HostNotRegistered,
)
from minecraft.skins import render_face
from minecraft.mojang import get_uuid

DEFAULT_PORT = 25565


def merge_images(files, output_path):
    """
    Merge two images into one vertically
    """

    images = []
    width = 0
    height = 0
    for file in files:
        tmp = Image.open(file)
        images += [tmp]
        (w, h) = tmp.size
        width = w
        height += h

    result = Image.new("RGB", (width, height))

    delta_h = height / len(images)
    for i, image in enumerate(images):
        result.paste(im=image, box=(0, int(delta_h) * i))

    result.save(output_path)


def parse_addr(addr):
    if len(addr.split(":")) == 2:
        return addr
    else:
        # assume default port
        return f"{addr}:{DEFAULT_PORT}"


def get_server(addr):
    # TODO test if bedrock?
    server = JavaServer.lookup(parse_addr(addr))
    return server


def parse_host(addr):
    """Parse into just host"""
    parts = addr.split(":")
    if len(parts) > 2:
        return parts[0]
    elif len(parts) == 2:
        if not parts[1] == str(DEFAULT_PORT):
            # non standard port, so include it
            return addr
    return parts[0]


def connect_alpha(addr):
    """
    since alpha doesnt have the same protocol, we will just
    try to connect to the port, and assume if the port is open that
    the server is running
    """
    print("connecting to alpha server addr:", addr)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        host, port = addr.split(":")
        s.connect((host, int(port)))
    except:
        return False
    return True


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


assets = [
    "minecraft.otf",
    "minecraft_bold.otf",
    "minecraft_italic.otf",
    "minecraft_bolditalic.otf",
    "default.png",
]


def load_assets():
    for asset in assets:
        shutil.copyfile(f"./public/{asset}", f"/tmp/{asset}")


def unload_assets():
    for asset in assets:
        os.remove(f"/tmp/{asset}")


def servers_status(
    output_path="/tmp/", addrs=[host_to_addr(hosts_get_active())], options={}
):
    if "all" in options and options["all"]:
        addrs = hosts_to_addrs()

    files = []
    for server in addrs:
        files += [server_status(output_path=output_path, addr=server, options=options)]

    path = f"/tmp/{time.time()}.png"
    merge_images(files, path)
    return path


def server_status(
    output_path="/tmp/", addr=host_to_addr(hosts_get_active()), options={}
):
    motd_html, favicon, players = [None] * 3
    addr = parse_addr(addr)
    name = parse_host(addr)

    alpha = False
    # lookup name and check if server is alpha
    try:
        host = host_get_details(addr)
        print(host, addr)
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
        if alpha and connect_alpha(addr):
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


def generate_player_tab(username, uuid):
    image_url = render_face(uuid)
    return f'<div class="player"> <img src="{image_url}" /><div>{username}</div></div>'


def generate_cols(players):
    # TODO balance out the cols?
    items = []
    for player in players:
        uuid = get_uuid(player)
        items += [generate_player_tab("njasi69", uuid)]
    return "".join(items)


def server_online(addr=host_to_addr(hosts_get_active())):
    srv = get_server(addr)
    status = srv.status()

    # generate_cols(status.players)
