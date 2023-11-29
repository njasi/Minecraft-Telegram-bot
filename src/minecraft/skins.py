# expected more to go here and i dont feel like combining files

def render_url(uuid):
    """
    realized the telegram bot can hande loading images from a url
    so the function is quite small lol
    """
    API_ENDPT = "https://nmsr.nickac.dev/fullbody/{}"
    return API_ENDPT.format(uuid)
