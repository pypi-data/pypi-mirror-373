#!/usr/bin/env python3
"""using tkinter to show frames"""
import tkinter as tk
from argparse import ArgumentParser, Namespace
from PIL import Image, ImageTk
import time
from queue import Queue
import threading
from datetime import datetime

from vre_video.utils import logger, image_add_text, mean
from vre_video import VREVideo

class CircularBuffer(list):
    def __init__(self, maxlen: int):
        self.maxlen = maxlen
        self.logical_len = 0
        super().__init__()

    def append(self, object):
        if len(self) < self.maxlen:
            super().append(object)
        else:
            self[self.logical_len % self.maxlen] = object
        self.logical_len += 1

    def clear(self):
        super().clear()
        self.logical_len = 0

# TODO: get rid of this wrapper
class VideoWrapper(VREVideo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fps_multiplier: float = 1.0
        self._current_frame: int = 0
        self.is_paused: bool = False

    @property
    def current_frame(self):
        return self._current_frame

    @current_frame.setter
    def current_frame(self, current_frame: int):
        if not 0 <= current_frame < len(self):
            logger.info(f"Frame {current_frame} wanted which is wrong. Reset to 0")
            current_frame = 0
        self._current_frame = int(current_frame)

class Window(threading.Thread):
    """with the help of the chat-ge-pe-tees"""
    def __init__(self, queue: Queue, video: VideoWrapper):
        super().__init__()
        self.queue = queue
        self.video = video
        self.show_stats = True
        self.fps_cnt = CircularBuffer(maxlen=100)

    def on_key_press(self, e: tk.Event):
        if e.char == "-":
            self.video.fps_multiplier = max(self.video.fps_multiplier / 2, 0.25)
            logger.info(f"Speed: {self.video.fps_multiplier}x")
        if e.char == "=":
            self.video.fps_multiplier = min(self.video.fps_multiplier * 2, 4.0)
            logger.info(f"Speed: {self.video.fps_multiplier}x")
        if e.keycode == 9: # esc
            self.root.destroy()
        if e.keycode == 65: # space
            self.video.is_paused = not self.video.is_paused
        if e.keycode == 113: # left arrow -> jump half a second back
            logger.debug((self.video.current_frame, round(self.video.current_frame - self.video.fps // 3)))
            self.video.current_frame = self.video.current_frame - self.video.fps // 3
        if e.keycode == 114: # right arrow -> jump half a second forward
            logger.debug((self.video.current_frame, round(self.video.current_frame + self.video.fps // 3)))
            self.video.current_frame = self.video.current_frame + self.video.fps // 3
        if e.char == "i":
            self.show_stats = not self.show_stats

    def run(self):
        self.root = tk.Tk()
        self.root.title(self.video.path)
        self.canvas = tk.Canvas(self.root, width=self.video.frame_shape[1], height=self.video.frame_shape[0])
        self.canvas.pack()
        self.canvas.bind("<KeyPress>", self.on_key_press)
        self.canvas.focus_set()

        while True:
            self.root.update()
            now = datetime.now()
            img_arr = self.queue.get(block=True)
            if self.show_stats:
                font_size = max(10, self.video.frame_shape[1] // 50)
                img_arr = image_add_text(
                    img_arr, f"Frame: {self.video.current_frame}. Avg fps: {mean(self.fps_cnt):.2f}",
                    position=(0, 18), font_size_px=font_size, font_color=(255, 255, 255)
                )
            photo = ImageTk.PhotoImage(image=Image.fromarray(img_arr))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            if self.show_stats and not self.video.is_paused:
                took = (datetime.now() - now).total_seconds()
                self.fps_cnt.append(1 / took)

def read_loop(video: VideoWrapper, q: Queue):
    """simply reads the current frame as given by video.current_frame. This can be updated by the gui thread"""
    while True:
        try:
            q.put(video[video.current_frame], timeout=0.5)
        except Exception as e:
            logger.info(f"Program closed: {e}")
            exit(0)

        next_frame = video.current_frame if video.is_paused else (video.current_frame + 1) % len(video)
        video.current_frame = next_frame
        time.sleep(1 / (video.fps * video.fps_multiplier))

def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("video_path")
    parser.add_argument("--input_size", nargs=2, type=int)
    args = parser.parse_args()
    return args

def main(args: Namespace):
    q = Queue(maxsize=1)
    video = VideoWrapper(args.video_path, resolution=args.input_size)
    # just start the thread and don't think about join.
    Window(q, video).start()
    read_loop(video, q)

if __name__ == "__main__":
    main(get_args())
