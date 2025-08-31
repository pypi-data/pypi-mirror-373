"""utils"""
from pathlib import Path
from typing import Any
from urllib.request import urlretrieve
import os
import numpy as np
from tqdm import tqdm
from loggez import make_logger
from PIL import Image, ImageDraw, ImageFont

logger = make_logger("VRE_VIDEO")

def image_write(file: np.ndarray, path: str):
    """PIL image writer"""
    assert file.min() >= 0 and file.max() <= 255
    img = Image.fromarray(file.astype(np.uint8), "RGB")
    img.save(path)

def image_read(path: str) -> np.ndarray:
    """PIL image reader"""
    # TODO: for grayscale, this returns a RGB image too
    img_pil = Image.open(path)
    img_np = np.array(img_pil, dtype=np.uint8)
    # grayscale -> 3 gray channels repeated.
    if img_pil.mode == "L":
        return np.repeat(img_np[..., None], 3, axis=-1)
    # RGB or RGBA
    return img_np[..., 0:3]

def image_add_text(image_np: np.ndarray, text: str, position: tuple[int, int], font_size_px: int,
                   font_color: tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
    """Adds text to a NumPy image array at the specified position with the specified font size."""
    image = Image.fromarray(image_np)
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", font_size_px)
    except IOError:
        font = ImageFont.load_default(font_size_px)
    draw.text(position, text, font=font, fill=font_color)
    return np.array(image)

def fetch(url: str, dst: str):
    """fetches data and stores locally with pbar"""
    assert not Path(dst).exists(), f"'{dst}' exists (or is a dir). Remove first or provide destination file path + name"
    class DownloadProgressBar(tqdm):
        """requests + tqdm"""
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs, disable=os.getenv("VRE_VIDEO_PBAR", "1") == "0")

        def update_to(self, b=1, bsize=1, tsize=None):
            """Callback from tqdm"""
            if tsize is not None:
                self.total = tsize
            self.update(b * bsize - self.n)

    with DownloadProgressBar(unit="B", unit_scale=True, miniters=1, desc=Path(dst).name) as t:
        try:
            urlretrieve(url, filename=dst, reporthook=t.update_to)
        except Exception as e:
            logger.info(f"Failed to download '{url}' to '{dst}'")
            raise e

def mean(x: list[int | float]) -> float:
    """mean of a list"""
    return sum(x) / len(x) if len(x) > 0 else 0

def parsed_str_type(item: Any) -> str:
    """Given an object with a type of the format: <class 'A.B.C.D'>, parse it and return 'A.B.C.D'"""
    return str(type(item)).rsplit(".", maxsplit=1)[-1][0:-2]
