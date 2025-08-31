"""init file"""
from pathlib import Path
import sys
from io import IOBase
import numpy as np

from .frame_reader import FrameReader
from .pil_frame_reader import PILFrameReader
from .numpy_frame_reader import NumpyFrameReader
from .ffmpeg_frame_reader import FFmpegFrameReader
from .fd_frame_reader import FdFrameReader

def build_frame_reader(source: str | Path | FrameReader | list[np.ndarray] | np.ndarray | IOBase,
                       **kwargs) -> FrameReader:
    """builds the frame reader given a source path for a VREVideo"""
    if isinstance(source, FrameReader):
        return source
    # pylint: disable=not-an-iterable
    if isinstance(source, np.ndarray) or (isinstance(source, list) and all(isinstance(x, np.ndarray) for x in source)):
        return NumpyFrameReader(source, **kwargs)
    if isinstance(source, IOBase):
        return FdFrameReader(source, **kwargs)
    if isinstance(source, str) and source == "-":
        return FdFrameReader(sys.stdin.buffer, **kwargs)
    if Path(source).is_dir():
        suffixes = list({x.suffix for x in Path(source).iterdir()})
        assert len(suffixes) == 1, suffixes
        if suffixes[0] == ".png":
            return PILFrameReader(source, **kwargs)
        if suffixes[0] in (".npy", ".npz"):
            return NumpyFrameReader(source, **kwargs)
    # Otherwise, let ffmpeg handle it and it'll throw on errors.
    return FFmpegFrameReader(source, **kwargs)
