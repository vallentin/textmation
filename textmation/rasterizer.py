#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import chain
from operator import attrgetter
from enum import IntEnum

from PIL import Image as _Image
from PIL import ImageDraw as _ImageDraw

from .properties import Color, Point, Size, Rect


class ResamplingFilter(IntEnum):
	Nearest = _Image.NEAREST
	Bilinear = _Image.BILINEAR


def _is_opaque(image):
	assert image.mode in ("RGB", "RGBA")

	if image.mode == "RGB":
		return True

	for _, _, _, a in image.getdata():
		if a != 255:
			return False

	return True


class Image:
	@staticmethod
	def new(size, background=Color(0, 0, 0)):
		assert isinstance(size, Size) and size.area > 0
		assert isinstance(background, Color)
		image = _Image.new("RGBA", tuple(size), tuple(background))
		return Image(image)

	@staticmethod
	def load(filename):
		image = _Image.open(filename)
		image.load()
		return Image(image)

	@staticmethod
	def save_gif(filename, frames, frame_rate):
		assert len(frames) > 0

		frames = list(map(attrgetter("_image"), frames))

		frames[0].save(
			filename,
			append_images=frames[1:],
			save_all=True,
			duration=1000 / frame_rate,
			loop=0,
			optimize=False)

	def __init__(self, image):
		self._image = image
		self._opaque = None

	@property
	def size(self):
		return Size(*self._image.size)

	@property
	def width(self):
		return self._image.width

	@property
	def height(self):
		return self._image.height

	@property
	def opaque(self):
		if self._opaque is None:
			self._opaque = _is_opaque(self._image)
		return self._opaque

	def save(self, filename):
		self._image.save(filename)

	def copy(self):
		return Image(self._image.copy())

	def resize(self, size, filter=ResamplingFilter.Nearest):
		assert isinstance(size, Size) and size.area > 0
		if self.size == size:
			return
		self._image = self._image.resize(size, filter)
		return self

	def resized(self, size, filter=ResamplingFilter.Nearest):
		return self.copy().resize(size, filter)

	def paste(self, image, bounds=None, *, alpha_composite=False, filter=ResamplingFilter.Nearest):
		if bounds is None:
			bounds = image.size
		if isinstance(bounds, Point):
			bounds = Rect(bounds, image.size)
		elif isinstance(bounds, Size):
			bounds = Rect(bounds)
		assert isinstance(bounds, Rect)

		if image.size != bounds.size:
			image = image.resized(bounds.size, filter)

		alpha_composite = alpha_composite and not image.opaque

		x, y, x2, y2 = map(int, chain(bounds.min, bounds.max))

		if alpha_composite:
			_image = _Image.new("RGBA", tuple(self.size), (0, 0, 0, 0))
			_image.paste(image._image, (x, y, x2, y2))
			self._image = _Image.alpha_composite(self._image, _image)
		else:
			self._image.paste(image._image, (x, y, x2, y2))

	def draw_rect(self, bounds, color):
		assert isinstance(bounds, Rect)
		assert isinstance(color, Color)

		x, y, x2, y2 = map(int, chain(bounds.min, bounds.max))

		if color.alpha == 255:
			draw = _ImageDraw.Draw(self._image, "RGBA")
			draw.rectangle((x, y, x2, y2), fill=tuple(map(int, color)))
		else:
			image = _Image.new("RGBA", self._image.size, (0, 0, 0, 0))
			draw = _ImageDraw.Draw(image, "RGBA")
			draw.rectangle((x, y, x2, y2), fill=tuple(map(int, color)))
			self._image = _Image.alpha_composite(self._image, image)
