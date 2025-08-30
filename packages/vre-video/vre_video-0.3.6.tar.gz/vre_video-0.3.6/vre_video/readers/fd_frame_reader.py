"""
fd_frame_reader - module for reading from a file descriptor (like stdin). To be used with external generating data
tool like ffmpeg (i.e. for webcams) and linux pipes.
"""
from io import IOBase
from threading import Lock, Thread
import numpy as np
from .frame_reader import FrameReader

from ..utils import logger

class FdFrameReader(FrameReader):
    """Implements FrameReader that reads from an io stream (like stdin). Can be used with linux pipes."""
    def __init__(self, data: IOBase, resolution: tuple[int, int]=(360, 1280), fps: int=30, async_worker: bool=False):
        assert isinstance(data, IOBase), type(data)
        super().__init__()
        self.data = data
        self._fps = fps
        self.resolution = (self.height, self.width) = resolution
        self.async_worker = async_worker

        self.lock = Lock()
        self.current_frame: np.ndarray | None = np.zeros((*resolution, 3), dtype=np.uint8)
        if self.async_worker:
            Thread(target=self._read_frame_worker, daemon=True).start()

    @property
    def shape(self) -> tuple[int, int, int, int]:
        return (1, self.height, self.width, 3)

    @property
    def fps(self):
        return self._fps

    @property
    def path(self) -> str:
        return str(self.data)

    def _read_one_frame(self) -> np.ndarray:
        raw_frame, frame = None, None
        try:
            raw_frame = self.data.read(self.width * self.height * 3)
        except ValueError as e:
            if str(e) not in ("I/O operation on closed file", "read of closed file"):
                raise e
        if raw_frame is not None and len(raw_frame) != 0:
            frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((self.height, self.width, 3))
        return frame

    def _read_frame_worker(self):
        """note: we need to use a thread here otherwise ffmpeg is too fast for our sync reader"""
        while True:
            frame = self._read_one_frame()
            if frame is None:
                break
            with self.lock:
                self.current_frame = frame
        logger.debug("read frame worked closed")

    def __getitem__(self, ix: int | list[int] | np.ndarray | slice) -> np.ndarray:
        if self.async_worker is False:
            frame = self._read_one_frame()
        else:
            with self.lock:
                frame = self.current_frame

        if frame is None:
            raise StopIteration
        if isinstance(ix, slice):
            assert (ix.start - ix.stop) == 1, f"cannot have batches in fd reader, got: {list(ix)}"
            ix = [0]
        if isinstance(ix, (list, np.ndarray)):
            assert len(ix) == 1, f"cannot have batches in fd reader, got: {ix}"
            frame = frame[None] # return a batch of one for other tools
        return frame
