# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-04-22 17:27:47
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Image methods.
"""


from typing import Any
from io import BytesIO
from qrcode import make as qrcode_make
from qrcode.image.pil import PilImage
from PIL.Image import open as pil_open, LANCZOS
from captcha.image import ImageCaptcha

from .rmonkey import monkey_path_pil_image_get_bytes
from .ros import File
from .rrand import randchar


__all__ = (
    'Image',
    'encode_qrcode',
    'decode_qrcode',
    'compress_image',
    'to_pil_image',
    'generate_captcha_image'
)


# Monkey path.
Image_ = monkey_path_pil_image_get_bytes()
Image = Image_


def encode_qrcode(text: str, path: str | None = None) -> bytes:
    """
    Encoding text to QR code image.

    Parameters
    ----------
    text : Text.
    path : File save path.
        - `None`: Not save.

    Returns
    -------
    Image bytes data.
    """

    # Encode.
    image: PilImage = qrcode_make(text)

    # Extract.
    bytes_io = BytesIO()
    image.save(bytes_io, 'JPEG')
    file_bytes = bytes_io.getvalue()

    # Save.
    if path is not None:
        file = File(path)
        file.write(file_bytes)

    return file_bytes


def decode_qrcode(image: str | bytes) -> list[str]:
    """
    Decoding QR code or bar code image.

    Parameters
    ----------
    image : Image bytes data or image file path.

    Returns
    -------
    QR code or bar code text list.
    """

    # Import.
    from pyzbar.pyzbar import decode as pyzbar_decode

    # Check.
    if isinstance(pyzbar_decode, BaseException):
        raise pyzbar_decode

    # Handle parameter.
    if type(image) in (bytes, bytearray):
        image = BytesIO(image)

    # Decode.
    image = pil_open(image)
    qrcodes_data = pyzbar_decode(image)

    # Convert.
    texts = [
        data.data.decode()
        for data in qrcodes_data
    ]

    return texts


def compress_image(
    input_image: str | bytes,
    ouput_image: str | None = None,
    target_size: float = 0.5,
    rate: int = 5,
    reduce: bool = False,
    max_quality: int = 75,
    min_quality: int = 0
) -> bytes | None:
    """
    Compress image file.

    Parameters
    ----------
    input_image : Input source image data.
        - `str`: Source image read file path.
        - `bytes`: Source image bytes data.
    output_image : Output compressed image data.
        - `None`: Return compressed image bytes data.
        - `str`: Compressed image file save path, no return.
    target_size : Compressed target size.
        - `value < 1`: Not more than this size ratio.
        - `value > 1`: Not more than this value, unit is KB.
    rate : Compressed iteration rate of quality and resolution.
    reduce : If target size is not completed, whether reduce image resolution for compression.
    max_quality : Iteration start image quality rate.
    min_quality : Iteration cutoff image quality rate.

    Returns
    -------
    Compressed image bytes data.
    """

    # Handle parameter.
    if type(input_image) == str:
        file = File(input_image)
        input_image = file.str
    now_size = len(input_image)
    if target_size < 1:
        target_size = now_size * target_size
    else:
        target_size *= 1024

    # Read image.
    bytesio = BytesIO(input_image)
    image = pil_open(bytesio)
    image = image.convert('RGB')

    # Step compress.
    quality = max_quality
    while now_size > target_size and quality >= min_quality:
        bytesio = BytesIO()
        image.save(bytesio, 'JPEG', quality=quality)
        now_size = len(bytesio.read())
        quality -= rate

    # Step reduce.
    if reduce:
        ratio = 1 - rate / 100
        while now_size > target_size:
            bytesio = BytesIO()
            resize = image.size[0] * ratio, image.size[1] * ratio
            image.thumbnail(resize, LANCZOS)
            image.save(bytesio, 'JPEG', quality=min_quality)
            now_size = len(bytesio.read())
            ratio -= rate / 100

    # Return.
    content = bytesio.read()

    ## Return file bytes data.
    if ouput_image is None:
        return content

    ## Save file and return path.
    else:
        file = File(ouput_image)
        file(content)


def to_pil_image(source: str | bytes) -> Image:
    """
    Get `Image` instance of `PIL` package.

    Parameters
    ----------
    source : Image source data.
        - `str`: Image file path.
        - `bytes`: Image bytes data.

    Returns
    -------
    `Image` instance.
    """

    # File path.
    if type(source) == str:
        pil_image = pil_open(source)

    # Bytes data.
    if type(source) in (bytes, bytearray):
        bytes_io = BytesIO(source)
        pil_image = pil_open(bytes_io)

    return pil_image


def generate_captcha_image(
    text: int | str | None = None,
    path: str | None = None,
    **kwargs: Any
) -> bytes:
    """
    Generate captcha image, based `captcha` package.

    Parameters
    ----------
    text : Text, contains digits and Uppercase letters and lowercase letters.
        - `None`: Random five characters.
        - `int`: Given length Random characters.
        - `str`: Given characters.
    path : File save path.
        - `None`: Not save.
    kwargs : `ImageCaptcha` Parameters.

    Returns
    -------
    Captcha image bytes data.
    """

    # Handle parameter.
    text = text or 5
    if type(text) == int:
        text = randchar(text, False)

    # Generate.
    default_kwargs = {
        'width': 240,
        'height': 90,
        'font_sizes': (61, 75, 84)
    }
    default_kwargs.update(kwargs)
    icaptcha = ImageCaptcha(**default_kwargs)
    image: Image = icaptcha.generate_image(text)
    file_bytes = image.get_bytes()

    # Save.
    if path is not None:
        file = File(path)
        file.write(file_bytes)

    return file_bytes
