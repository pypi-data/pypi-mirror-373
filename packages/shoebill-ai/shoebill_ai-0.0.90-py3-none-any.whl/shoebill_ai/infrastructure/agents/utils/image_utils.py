import base64
import io

from PIL import Image, ImageOps


def encode_image(image_path: str, image_format: str = "jpeg", max_size: tuple[float,float] = (1024, 1024),
                 quality: int = 95) -> str:
    """
    Encode an image to base64 without data URI prefix.

    Args:
        image_path: The path to the image file to encode.
        image_format: The format to save the image as (default: jpeg).
        max_size: Maximum dimensions for the image.
        quality: Quality setting for JPEG and WebP formats.

    Returns:
        str: Base64-encoded image data without data URI prefix.
    """
    image = Image.open(image_path)
    image = image.copy()
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA" if image_format.lower() in ("png", "webp") else "RGB")
    buffer = io.BytesIO()
    image_format = image_format.lower()
    if image_format in ("jpeg", "jpg"):
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
    elif image_format == "webp":
        image.save(buffer, format="WEBP", quality=quality, method=6)
    else:
        image.save(buffer, format=image_format.upper())
    buffer.seek(0, 2)
    if buffer.tell() == 0:
        raise ValueError("Image buffer is empty after saving")
    buffer.seek(0)
    encoding = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return encoding