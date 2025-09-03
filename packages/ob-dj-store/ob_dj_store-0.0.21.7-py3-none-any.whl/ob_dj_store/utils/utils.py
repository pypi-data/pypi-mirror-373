import logging
import os
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.timezone import now
from PIL import Image, UnidentifiedImageError
from pilkit.processors import ResizeToFill

logger = logging.getLogger(__name__)


def resize_image(image, dim: dict, size_name: str, image_name: str = None):
    try:
        img = Image.open(image)
    except UnidentifiedImageError as e:
        logger.error(e)
        return None
    width, height = dim.values()
    processor = ResizeToFill(width=width, height=height)
    new_img = processor.process(img)
    filename, extension = os.path.splitext(image.name)
    extension = extension.lower()
    if extension == ".png":
        content_type = "image/png"
        img_format = "PNG"
    else:
        content_type = "image/jpeg"
        img_format = "JPEG"
    output = BytesIO()
    if new_img.mode in ("RGBA", "P"):
        new_img = new_img.convert("RGB")
    new_img.save(output, format=img_format, quality=70)
    output.seek(0)
    if not image_name:
        image_name = filename
    new_image = InMemoryUploadedFile(
        output,
        "ImageField",
        f"{image_name}_{int(now().timestamp())}_{size_name}.{img_format.lower()}",
        content_type,
        output.__sizeof__(),
        None,
    )
    return new_image
