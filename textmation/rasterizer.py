#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import chain
from operator import attrgetter
from enum import Enum, IntEnum, IntFlag

from PIL import Image as _Image
from PIL import ImageDraw as _ImageDraw
from PIL import ImageFont as _ImageFont

from .datatypes import Vec2, Vec4, Color
from .datatypes import Point, Size, Rect


_fonts = {}


class ResamplingFilter(IntEnum):
	Nearest = _Image.NEAREST
	Bilinear = _Image.BILINEAR


class Anchor(IntFlag):
	Left = 1
	CenterX = 2
	Right = 4
	Top = 8
	CenterY = 16
	Bottom = 32
	Center = CenterX | CenterY


class Alignment(Enum):
	Left = "left"
	Center = "center"
	Right = "right"


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
	def new(size, background=Color(0, 0, 0, 255)):
		assert isinstance(size, Size) and size.area > 0
		assert isinstance(background, (Vec4, Color))
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

	def draw_rect(self, bounds, fill, outline=Color(0, 0, 0, 0), outline_width=1):
		assert isinstance(bounds, Rect)
		assert isinstance(fill, (Vec4, Color))
		assert isinstance(outline, (Vec4, Color))

		if fill.a == 0 and outline.a == 0:
			return

		x, y, x2, y2 = map(int, chain(bounds.min, bounds.max))

		# Reference: https://github.com/python-pillow/Pillow/issues/1668
		x2 -= 1
		y2 -= 1

		fill = tuple(map(int, fill))
		outline = tuple(map(int, outline))

		if fill[3] == 255:
			draw = _ImageDraw.Draw(self._image, "RGBA")
			draw.rectangle((x, y, x2, y2), fill=fill)
		elif fill[3] > 0:
			image = _Image.new("RGBA", self._image.size, (0, 0, 0, 0))
			draw = _ImageDraw.Draw(image, "RGBA")
			draw.rectangle((x, y, x2, y2), fill=fill)
			self._image = _Image.alpha_composite(self._image, image)

		if outline[3] == 255:
			draw = _ImageDraw.Draw(self._image, "RGBA")
			draw.rectangle((x, y, x2, y2), outline=outline, width=int(outline_width))
		elif outline[3] > 0:
			image = _Image.new("RGBA", self._image.size, (0, 0, 0, 0))
			draw = _ImageDraw.Draw(image, "RGBA")
			draw.rectangle((x, y, x2, y2), outline=outline, width=int(outline_width))
			self._image = _Image.alpha_composite(self._image, image)

	def draw_circle(self, center, radius, fill, outline=Color(0, 0, 0, 0), outline_width=1):
		self.draw_ellipse(center, radius, radius, fill, outline, outline_width)

	def draw_ellipse(self, center, radius_x, radius_y, fill, outline=Color(0, 0, 0, 0), outline_width=1):
		assert isinstance(center, (Vec2, Point))
		assert isinstance(fill, (Vec4, Color))
		assert isinstance(outline, (Vec4, Color))

		if fill.a == 0 and outline.a == 0:
			return

		x, y, x2, y2 = center.x - radius_x, center.y - radius_y, center.x + radius_x, center.y + radius_y

		fill = tuple(map(int, fill))
		outline = tuple(map(int, outline))

		if fill[3] == 255:
			draw = _ImageDraw.Draw(self._image, "RGBA")
			draw.ellipse((x, y, x2, y2), fill=fill)
		elif fill[3] > 0:
			image = _Image.new("RGBA", self._image.size, (0, 0, 0, 0))
			draw = _ImageDraw.Draw(image, "RGBA")
			draw.ellipse((x, y, x2, y2), fill=fill)
			self._image = _Image.alpha_composite(self._image, image)

		if outline[3] == 255:
			draw = _ImageDraw.Draw(self._image, "RGBA")
			draw.ellipse((x, y, x2, y2), outline=outline, width=int(outline_width))
		elif outline[3] > 0:
			image = _Image.new("RGBA", self._image.size, (0, 0, 0, 0))
			draw = _ImageDraw.Draw(image, "RGBA")
			draw.ellipse((x, y, x2, y2), outline=outline, width=int(outline_width))
			self._image = _Image.alpha_composite(self._image, image)

	def draw_line(self, p1, p2, fill, width=1):
		assert isinstance(p1, (Vec2, Point))
		assert isinstance(p2, (Vec2, Point))
		assert isinstance(fill, (Vec4, Color))

		if fill.a == 0:
			return

		x, y, x2, y2 = p1.x, p1.y, p2.x, p2.y

		if fill.a == 255:
			draw = _ImageDraw.Draw(self._image, "RGBA")
			draw.line((x, y, x2, y2), fill=tuple(map(int, fill)), width=int(width))
		else:
			image = _Image.new("RGBA", self._image.size, (0, 0, 0, 0))
			draw = _ImageDraw.Draw(image, "RGBA")
			draw.line((x, y, x2, y2), fill=tuple(map(int, fill)), width=int(width))
			self._image = _Image.alpha_composite(self._image, image)

	def draw_text(self, text, position, fill, font, anchor=Anchor.Center, alignment=Alignment.Left):
		assert isinstance(text, str)
		assert isinstance(position, Point)
		assert isinstance(fill, Color)
		assert isinstance(font, Font)
		assert isinstance(alignment, Alignment)

		if fill.a == 0:
			return

		text_width, text_height = font.measure_text(text)
		text_offset_x, text_offset_y = font.get_offset(text)

		x, y = position

		if anchor & Anchor.CenterX:
			x -= (text_width + text_offset_x) / 2
		elif anchor & Anchor.Right:
			x -= text_width + text_offset_x

		if anchor & Anchor.CenterY:
			y -= (text_height + text_offset_y) / 2
		elif anchor & Anchor.Bottom:
			y -= text_height + text_offset_y

		position = x, y

		if fill.a == 255:
			draw = _ImageDraw.Draw(self._image, "RGBA")
			draw.text(position, text, fill=tuple(map(int, fill)), font=font._font, align=alignment.value)
		else:
			image = _Image.new("RGBA", self._image.size, (0, 0, 0, 0))
			draw = _ImageDraw.Draw(image, "RGBA")
			draw.text(position, text, fill=tuple(map(int, fill)), font=font._font, align=alignment.value)
			self._image = _Image.alpha_composite(self._image, image)


class Font:
	@staticmethod
	def load(font, size):
		size = int(size)
		try:
			return _fonts[font, size]
		except KeyError:
			font = _ImageFont.truetype(font, size)
			_fonts[font, size] = font
			return Font(font, size)

	def __init__(self, font, size):
		self._font = font
		self._size = size

	@property
	def size(self):
		return self._size

	def measure_line(self, line):
		return self._font.getsize(line)

	def measure_lines(self, text):
		for line in text.splitlines():
			yield self.measure_line(line)

	def measure_text(self, text, spacing=4):
		width, height = 0, 0

		for i, (w, h) in enumerate(self.measure_lines(text)):
			width = max(width, w)
			height += h
			if i > 0:
				height += spacing

		return width, height

	def get_offset(self, text):
		return self._font.getoffset(text)
