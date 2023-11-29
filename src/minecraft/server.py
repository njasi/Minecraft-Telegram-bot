# server related methods, ie pinging server etc
import os
import shutil
import time
from PIL import Image
from html2image import Html2Image
from mcstatus import JavaServer
from minecraft.hosts import host_get_pretty_name, hosts_to_addrs

HOSTNAME = os.environ.get("SERVER_HOST")
PORT = os.environ.get("SERVER_PORT")
MAIN_SERVER = f"{HOSTNAME}:{PORT}"
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
    print("ADDR:", parse_addr(addr))
    server = JavaServer.lookup(parse_addr(addr))
    return server


def parse_addr(addr):
    """Parse into just host"""
    # TODO add mapping to known hosts
    parts = addr.split(":")
    if len(parts) > 2:
        return parts[0]
    elif len(parts) == 2:
        if not parts[1] == str(DEFAULT_PORT):
            # non standard port, so include it
            return addr
    return parts[0]


def server_ping(addr=MAIN_SERVER):
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


def servers_status(output_path="/tmp/", addrs=[MAIN_SERVER], options={}):
    print(options)
    if "all" in options and options["all"]:
        addrs = hosts_to_addrs()

    files = []
    for server in addrs:
        files += [server_status(output_path=output_path, addr=server, options=options)]

    path = f"/tmp/{time.time()}.png"
    merge_images(files, path)
    return path


def server_status(output_path="/tmp/", addr=MAIN_SERVER, options={}):
    motd_html, favicon, players = [None] * 3

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

    # lookup name in json
    name = addr
    if "host" not in options or not options["host"]:
        name = host_get_pretty_name(addr)
        print("NAME", name)
    name = parse_addr(name)

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


def online():
    pass
