from html2image import Html2Image
from data.hosts import (
    hosts_to_addrs,
    host_to_addr,
    hosts_get_active,
    host_get_details,
    HostNotRegistered,
)
from minecraft.skins import render_face
from minecraft.mojang import get_uuid
from minecraft.server import get_server

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


def render_online(addr=host_to_addr(hosts_get_active())):
    srv = get_server(addr)
    status = srv.status()

    # generate_cols(status.players)
