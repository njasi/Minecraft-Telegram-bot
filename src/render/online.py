from html2image import Html2Image
from data.hosts import (
    host_to_addr,
    hosts_get_active,
)
from minecraft.skins import render_face
from minecraft.mojang import get_uuid
from minecraft.server import get_server
from render.helpers import load_assets, unload_assets


def generate_player_tab(username, uuid):
    image_url = render_face(uuid)
    return f'<div class="player"> <img src="{image_url}" /><div>{username}</div></div>'


def generate_cols(players):
    # TODO balance out the cols?
    items = []
    for player in players:
        items += [generate_player_tab(player.name, player.id)]
    return "".join(items)


def render_online(addr=host_to_addr(hosts_get_active()), output_path="/tmp/"):
    srv = get_server(addr)
    status = srv.status()

    if status.players.sample is None:
        raise Exception("Server did not return player sample")

    cols = generate_cols(status.players.sample)

    # load renderer
    hti = Html2Image(output_path=output_path, size=(512, 110))

    # load in formatting from files
    wrapping = None
    css = None
    with open("./public/tablist.html") as file:
        wrapping = file.read()
    with open("./public/tablist.css") as file:
        css = file.read()

    file = f"{addr}_tablist.png"

    html = wrapping.format(cols)

    load_assets()
    hti.screenshot(html_str=html, css_str=css, save_as=file)
    unload_assets()

    return output_path + file
