#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import islice
from operator import attrgetter
from typing import Optional, Union, Tuple, List

from PIL import Image, ImageDraw


class Frame:
	def __init__(self, size: Tuple[int, int], color: Union[Tuple[int, int, int], Tuple[int, int, int, int]] = (0, 0, 0), format: str = "RGB"):
		self.size = size
		self.color = color
		self.duration = 200
		self.image = Image.new(format, size, color)
		self.draw = ImageDraw.Draw(self.image, "RGBA")

	def draw_rect(self,
			position: Tuple[Union[int, float], Union[int, float]],
			size: Tuple[Union[int, float], Union[int, float]],
			fill: Optional[Union[Tuple[int, int, int], Tuple[int, int, int, int], str]] = None,
			outline: Optional[Union[Tuple[int, int, int], Tuple[int, int, int, int], str]] = None,
			width: int = 0):
		x, y = position
		w, h = size
		x2 = x + w
		y2 = y + h
		self.draw.rectangle((x, y, x2, y2), fill=fill, outline=outline, width=width)

	def save(self, filename: str):
		self.image.save(filename)


class Frames:
	def __init__(self):
		self.frames: List[Frame] = []

	def add(self, frame: Frame):
		self.frames.append(frame)

	def __getitem__(self, index: int):
		return self.frames[index]

	def save(self, filename: str):
		assert len(self.frames) > 1
		assert all(self.frames[0].size == frame.size for frame in self.frames)

		self.frames[0].image.save(
			filename,
			format="GIF",
			append_images=map(attrgetter("image"), islice(self.frames, 1, None)),
			save_all=True,
			duration=list(map(attrgetter("duration"), self.frames)),
			loop=0,
			# https://github.com/python-pillow/Pillow/issues/2734
			optimize=False)


if __name__ == "__main__":
	frames = Frames()

	size = 400, 400
	frame_rate = 20

	rw, rh = 200, 200
	rx = size[0] / 2 - rw / 2
	ry = size[1] / 2 - rh / 2

	duration = 2 # seconds
	frame_count = frame_rate * duration

	for i in range(frame_count):
		t = i / (frame_count - 1)

		frame = Frame(size, (0, 0, 0))
		frame.duration = 1000 // frame_rate

		frame.draw_rect((rx, ry), (rw, rh), (255, 0, int(255 - t * 255)))

		frames.add(frame)

	for i in range(frame_count):
		t = i / (frame_count - 1)

		frame = Frame(size, (0, 0, 0))
		frame.duration = 1000 // frame_rate

		frame.draw_rect((rx, ry), (rw, rh), (255, 0, int(t * 255)))

		frames.add(frame)

	frames.save("output.gif")
