# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT


from quart import Blueprint
from PIL import Image
from random import randint
from io import BytesIO

image_provider_blueprint = Blueprint("image_provider", __name__)
"""Provides the capability to generate randomly colored 40 by 40 pixel images in various formats"""


def determine_format(filename):
    if filename.endswith("jpg"):
        return "JPEG", "image/jpeg"
    if filename.endswith("eps"):
        return "EPS", "image/eps"
    if filename.endswith("gif"):
        return "GIF", "image/gif"
    if filename.endswith("tiff"):
        return "TIFF", "image/tiff"
    if filename.endswith("webp"):
        return "WEBP", "image/webp"
    return "PNG", "image/png"


@image_provider_blueprint.get("/<filename>")
async def get_filename(filename):
    """Returns a random image. If filename ends with jpg, eps, gif, tiff, or webp an image of that type is returned otherwise png"""
    image_format, content_type = determine_format(filename)

    b = BytesIO()
    image = Image.new(
        "RGB", (40, 40), (randint(0, 255), randint(0, 255), randint(0, 255))
    )
    image.save(b, format=image_format)

    return b.getvalue(), 200, {"content-type": content_type}
