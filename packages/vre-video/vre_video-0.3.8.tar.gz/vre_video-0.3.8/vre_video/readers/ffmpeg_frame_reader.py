"""FFmpegFrameReader module"""
from pathlib import Path
from io import FileIO
import os
import json
import subprocess
import numpy as np

from .frame_reader import FrameReader
from ..utils import logger

class FFmpegFrameReader(FrameReader):
    """FFmpegFrameReader -- reads data from a video using ffmpeg"""
    def __init__(self, path: str | Path, cache_len: int = int(os.getenv("FFMPEG_FRAME_READER_CACHE_LEN", "100"))):
        super().__init__()
        self._path = self._build_path(path)
        assert self._path.exists(), f"Video '{self._path}' doesn't exist"
        self.probe_data, self.stream_info = self._run_ffprobe_get_data()

        self._fps: float | None = None
        self._shape: tuple[int, int, int, int] | None = None

        self.cache = []
        self.cache_max_len = cache_len
        self.cache_start_frame = None
        self.cache_end_frame = None

        self.process: subprocess.Popen | None = None
        self.log_file: FileIO | None = None

    @property
    def shape(self) -> tuple[int, int, int, int]:
        if self._shape is None:
            width = int(self.stream_info["width"])
            height = int(self.stream_info["height"])
            total_frames = self._build_total_frames()
            self._shape = (total_frames, height, width, 3)
        return self._shape

    @property
    def fps(self) -> float:
        if self._fps is None:
            self._fps = eval(self.stream_info["avg_frame_rate"]) # pylint: disable=eval-used
        return self._fps

    @property
    def path(self) -> str:
        return str(self._path)

    def get_one_frame(self, ix: int) -> np.ndarray:
        """Retrieve a frame from the video by frame number, using nearby frames caching."""
        assert isinstance(ix, int), type(ix)
        assert 0 <= ix < len(self), f"Frame out of bounds: {ix}. Len: {len(self)}"

        # Load new cache if the requested frame is outside the current cache range
        if self.cache_start_frame is None or not self.cache_start_frame <= ix < self.cache_end_frame:
            self._cache_frames(start_frame=ix)

        # Calculate the index within the cache
        return self.cache[ix - self.cache_start_frame]

    def _build_path(self, path: str | Path) -> Path:
        """Builds the path. Can also be a youtube video, not just a local path, but yt_dlp must be installed"""
        if (s_path := str(path)).startswith("http") and (s_path.find("youtube") != -1 or s_path.find("youtu.be") != -1):
            from yt_dlp import YoutubeDL # pylint: disable=import-outside-toplevel, import-error
            tmpfile = f"/tmp/{path}.mp4"
            if not Path(tmpfile).exists():
                with YoutubeDL({"format": "bv*", "outtmpl": tmpfile, "quiet": True,
                                "no_warnings": True, "noprogress": True}) as ydl:
                    ydl.download([s_path])
            path = tmpfile
        return Path(path)

    def _build_total_frames(self) -> int:
        """returns the number of frames of the vifdeo"""
        if "nb_frames" in self.stream_info:
            return int(float(self.stream_info["nb_frames"]))
        if "duration" in self.stream_info:
            duration_s = float(self.stream_info["duration"])
            return int(duration_s * self.fps)
        if self.stream_info.get("codec_name", "") == "h264":
            if "tags" in self.stream_info and "DURATION" in self.stream_info["tags"]:
                duration_str = self.stream_info["tags"]["DURATION"]
                h, m, s = [float(x) for x in duration_str.split(":")]
                duration_s = h * 60 * 60 + m * 60 + s
                return int(duration_s * self.fps)
        if self.stream_info.get("codec_name", "") == "vp9":
            if "format" in self.probe_data and "duration" in self.probe_data["format"]:
                duration_s = float(self.probe_data["format"]["duration"])
                return int(duration_s * self.fps)
        raise ValueError(f"Unknown video format. Stream info from ffmpeg: {self.stream_info}")

    def _start_ffmpeg_process(self, start_time: float) -> subprocess.Popen:
        """
        Start an ffmpeg process from the nearest keyframe to the requested start_time.
        This will load all frames from this keyframe to the next keyframe.
        """
        self._cleanup_if_needed()
        self.log_file = open(Path(self.path).with_suffix(".ffmpeg.log"), "w")
        cmd = [
            "ffmpeg",
            "-ss", str(start_time),
            "-i", str(self.path),
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "pipe:" # output to stdout
        ]
        logger.debug(f"Running '{' '.join(cmd)}' (log: {self.log_file.name})")
        self.process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=self.log_file)

    def _run_ffprobe_get_data(self) -> tuple[dict, dict]:
        cmd = [
            "ffprobe",
            "-v", "error",            # suppress unnecessary output
            "-select_streams", "v",   # select only video streams
            "-show_entries", "stream",  # show all stream fields
            "-show_entries", "format", # required for vp9
            "-of", "json",            # output format: JSON
            str(self.path)
        ]
        logger.debug(f"Running '{' '.join(cmd)}'")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        probe_data = json.loads(result.stdout)

        # Extract the first video stream
        stream_info = next((stream for stream in probe_data.get("streams", [])
                            if stream.get("codec_type") == "video"), None)
        return probe_data, stream_info

    def _cleanup_if_needed(self):
        if hasattr(self, "process") and self.process is not None: # hasattr in case the constructor throws on .exists()
            self.process.stdout.close()
            self.process.terminate()
        if hasattr(self, "log_file") and self.log_file is not None:
            self.log_file.close()
            self.log_file = None

    def _cache_frames(self, start_frame: int):
        """Cache all frames between the current keyframe and the next keyframe, starting at start_frame."""
        start_time = start_frame / self.fps
        self.cache = []
        if self.process is None or start_frame != self.cache_end_frame:
            self._start_ffmpeg_process(start_time)

        # Read frames until the end of the current keyframe range
        while True:
            in_bytes = self.process.stdout.read(self.shape[1] * self.shape[2] * 3)
            if not in_bytes or len(self.cache) > self.cache_max_len:
                break
            frame = np.frombuffer(in_bytes, np.uint8).reshape([self.shape[1], self.shape[2], 3])
            self.cache.append(frame)

        # Set cache boundaries in terms of frame numbers
        self.cache_start_frame = start_frame
        self.cache_end_frame = start_frame + len(self.cache)

    def __del__(self):
        self._cleanup_if_needed()

    def __getitem__(self, ix: int | list[int] | np.ndarray | slice) -> np.ndarray:
        if isinstance(ix, np.ndarray):
            return self[ix.tolist()]
        if isinstance(ix, list):
            return np.array([self[_ix] for _ix in ix])
        if isinstance(ix, slice):
            return np.array([self[_ix] for _ix in range(ix.start, ix.stop)])
        return self.get_one_frame(ix)
