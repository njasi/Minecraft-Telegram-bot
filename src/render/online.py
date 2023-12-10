from html2image import Html2Image
from data.hosts import (
    host_to_addr,
    hosts_get_active,
)
from minecraft.skins import render_face
from minecraft.mojang import get_uuid
from minecraft.server import get_server
from render.helpers import load_assets, unload_assets
import math

# sizes in pixels for getting a nice sized pic of the tablist

# height + width incuding padding / margin
PLAYER_CARD_WIDTH = 167
PLAYER_CARD_HEIGHT = 20
TABLIST_HEIGHT = 502
TABLIST_WIDTH = 502
TABLIST_PADDING = 5
# computed values
PLAYERS_PER_COL = math.floor(TABLIST_HEIGHT / PLAYER_CARD_WIDTH)
MAX_COLS = math.floor(TABLIST_WIDTH / PLAYER_CARD_WIDTH)


def get_size(player_count):
    """
    Using the above constants get the predicted size of the tablist,
    so we can send an image with little deadspace

    returns tupple (width, height)
    """
    width = (0,)
    height = 0

    num_cols = math.ceil(player_count / PLAYERS_PER_COL)

    if num_cols > MAX_COLS:
        return (
            TABLIST_WIDTH + TABLIST_PADDING * 2,
            TABLIST_HEIGHT + TABLIST_PADDING * 2,
        )
    elif num_cols > 1:
        return (
            num_cols * PLAYER_CARD_WIDTH + TABLIST_PADDING * 2,
            TABLIST_HEIGHT + TABLIST_PADDING * 2,
        )
    else:
        pass

    return width, height


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

    if status.players is None or status.players.sample is None:
        raise Exception("Server did not return player sample")

    cols = generate_cols(status.players.sample)

    # load renderer
    size = get_size(len(status.players.sample))
    hti = Html2Image(output_path=output_path, size=size)

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
