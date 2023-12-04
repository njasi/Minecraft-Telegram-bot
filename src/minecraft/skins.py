# all functions should be defined in a oneliner smh, sorry abt this file I got bored

"""generate render url functions"""
render_skin, render_face = [lambda u: "https://nmsr.nickac.dev/{}/{}".format(t, u) for t in ["fullbody", "face"]]