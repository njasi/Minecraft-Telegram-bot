import shutil
import os
from PIL import Image

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
