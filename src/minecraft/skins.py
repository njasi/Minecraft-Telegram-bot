# expected more to go here and i dont feel like combining files

API_ENDPT = "https://nmsr.nickac.dev/{}/{}"


def render_url(uuid):
    """
    realized the telegram bot can hande loading images from a url
    so the function is quite small lol
    """
    return API_ENDPT.format("fullbody", uuid)


def render_face(uuid):
    """
    get the face url for the tablist, which is rendered with html,
    so we can use the url directly.

    Note that this means we will ask html2image to wait a second to load them
    """
    return API_ENDPT.format("face", uuid)
