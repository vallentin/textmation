#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import tee
from operator import attrgetter
import os

from PIL import Image, ImageDraw, ImageChops, ImageFont

from scene import *


_point_table = (0,) + (255,) * 255


def pairwise(iterable, *, n=2):
	iterators = tee(iterable, n)
	for i in range(n):
		for _ in range(i):
			next(iterators[i])
	yield from zip(*iterators)


def iter_frame_time(duration, frame_rate, *, inclusive=False):
	frames = duration * frame_rate
	if inclusive:
		frames += 1

	for frame in range(frames):
		time = frame / frame_rate
		yield frame, time


class Frame:
	def __init__(self, size, background=(0, 0, 0)):
		if not isinstance(background, Color):
			assert isinstance(background, tuple)
			background = Color(*background)
		self.size = size
		self.background = background

	def save(self, filename):
		raise NotImplementedError

	def draw_rect(self, bounds, color):
		raise NotImplementedError

	def draw_text(self, text, position, color, font):
		raise NotImplementedError


class Renderer:
	def __init__(self):
		self.frames = []

	@property
	def _frame(self):
		return self.frames[-1]

	def _create_frame(self, size, background):
		raise NotImplementedError

	def _get_font(self, font, size):
		raise NotImplementedError

	def render(self, element):
		assert len(self.frames) == 0
		frame = self._render(element)
		assert len(self.frames) == 0
		assert isinstance(frame, Frame)
		return frame

	def _render(self, element):
		method = "_render_%s" % element.__class__.__name__
		visitor = getattr(self, method)
		return visitor(element)

	def _render_children(self, element):
		for child in element.children:
			self._render(child)

	def _render_Scene(self, scene):
		self.frames.append(self._create_frame(scene.size, scene.background))
		self._render_children(scene)
		return self.frames.pop()

	def _render_Rectangle(self, rect):
		self._frame.draw_rect(rect.bounds, rect.color)

	def _render_Text(self, text):
		font = self._get_font(text.font, text.font_size)
		self._frame.draw_text(text.text, text.position, text.color, font)


class PILFrame(Frame):
	def __init__(self, size, background=(0, 0, 0)):
		super().__init__(size, background)
		self.image = Image.new("RGBA", self.size, tuple(self.background))

	def save(self, filename):
		self.image.save(filename)

	def draw_rect(self, bounds, color):
		(x, y), (x2, y2) = bounds.min, bounds.max
		if color.alpha == 255:
			draw = ImageDraw.Draw(self.image, "RGBA")
			draw.rectangle((x, y, x2, y2), fill=tuple(map(int, color)))
		else:
			image = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
			draw = ImageDraw.Draw(image, "RGBA")
			draw.rectangle((x, y, x2, y2), fill=tuple(map(int, color)))
			self.image = Image.alpha_composite(self.image, image)

	def draw_text(self, text, position, color, font):
		if color.alpha == 255:
			draw = ImageDraw.Draw(self.image, "RGBA")
			draw.text(position, text, fill=tuple(map(int, color)), font=font)
		else:
			image = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
			draw = ImageDraw.Draw(image, "RGBA")
			draw.text(position, text, fill=tuple(map(int, color)), font=font)
			self.image = Image.alpha_composite(self.image, image)


class PILRenderer(Renderer):
	def __init__(self):
		super().__init__()
		self.fonts = {}

	def _create_frame(self, size, background):
		return PILFrame(size, background)

	def _get_font(self, font, size):
		size = int(size)
		try:
			return self.fonts[font, size]
		except KeyError:
			font = ImageFont.truetype(font, size)
			self.fonts[font, size] = font
			return font


def _save_gif(filename, frames, frame_rate):
	if isinstance(frames[0], PILFrame):
		frames = list(map(attrgetter("image"), frames))
	assert isinstance(frames[0], Image.Image)
	frames[0].save(
		filename,
		append_images=frames[1:],
		save_all=True,
		duration=1000 / frame_rate,
		loop=0,
		optimize=False)


def _render_difference(a, b):
	if isinstance(a, PILFrame):
		a = a.image
	if isinstance(b, PILFrame):
		b = b.image

	diff = ImageChops.difference(a, b)
	diff = diff.convert("L")
	diff = diff.point(_point_table)
	diff = diff.convert("RGB")

	return diff


if __name__ == "__main__":
	scene = Scene((400, 400))

	"""
	r1tl = Rectangle((10, 10, 85, 85), color=(255, 0, 0))
	r1tr = Rectangle((105, 10, 85, 85), color=(0, 255, 0))
	r1bl = Rectangle((10, 105, 85, 85), color=(0, 0, 255))
	r1br = Rectangle((105, 105, 85, 85), color=(255, 0, 255))

	scene.add_all((r1tl, r1tr, r1bl, r1br))

	a1tl = Animation("color.alpha")
	a1tl.add(Keyframe(0, 0))
	a1tl.add(Keyframe(1, 255))
	a1tl.add(Keyframe(2, 0))

	a1tr = Animation("color.alpha")
	a1tr.delay = 0.5
	a1tr.add(Keyframe(0, 0))
	a1tr.add(Keyframe(1, 255))
	a1tr.add(Keyframe(2, 0))

	a1bl = Animation("color.alpha")
	a1bl.delay = 1.0
	a1bl.add(Keyframe(0, 0))
	a1bl.add(Keyframe(1, 255))
	a1bl.add(Keyframe(2, 0))

	a1br = Animation("color.alpha")
	a1br.delay = 1.5
	a1br.add(Keyframe(0, 0))
	a1br.add(Keyframe(1, 255))
	a1br.add(Keyframe(2, 0))

	r1tl.add(a1tl)
	r1tr.add(a1tr)
	r1bl.add(a1bl)
	r1br.add(a1br)
	"""

	"""
	r2 = Rectangle((50, 50), (255, 255, 255))

	r2a1 = Animation("color")
	r2a1.add(Keyframe(0, Color(255, 255, 255)))
	r2a1.add(Keyframe(0.7, Color(255, 0, 0)))
	r2a1.add(Keyframe(1.4, Color(0, 255, 0)))
	r2a1.add(Keyframe(2.1, Color(0, 0, 255)))
	r2a1.add(Keyframe(2.8, Color(255, 0, 255)))
	r2a1.add(Keyframe(3.5, Color(255, 255, 255)))

	r2a2 = Animation("bounds.x")
	r2a2.add(Keyframe(0, 0))
	r2a2.add(Keyframe(1.75, 150))
	r2a2.add(Keyframe(3.5, 0))

	r2a3 = Animation("bounds.y")
	r2a3.add(Keyframe(0, 75))
	r2a3.add(Keyframe(0.875, 50))
	r2a3.add(Keyframe(1.75, 75))
	r2a3.add(Keyframe(2.625, 50))
	r2a3.add(Keyframe(3.5, 75))

	r2a4 = Animation("bounds.height")
	r2a4.add(Keyframe(0, 50))
	r2a4.add(Keyframe(0.875, 100))
	r2a4.add(Keyframe(1.75, 50))
	r2a4.add(Keyframe(2.625, 100))
	r2a4.add(Keyframe(3.5, 50))

	r2.add_all((r2a1, r2a2, r2a3, r2a4))

	scene.add(r2)
	"""

	t1 = Text("Hello World")

	t1.position = 20, 20
	t1.font, t1.font_size = "fonts/Montserrat-Regular.ttf", 32

	t1a1 = Animation("font_size")
	t1a1.add(Keyframe(0, 30))
	t1a1.add(Keyframe(1, 50))
	t1a1.add(Keyframe(2, 30))

	t1a2 = Animation("color.green")
	t1a2.add(Keyframe(0, 255))
	t1a2.add(Keyframe(1, 0))
	t1a2.add(Keyframe(2, 255))

	t1.add_all((t1a1, t1a2))

	scene.add(t1)

	renderer = PILRenderer()
	frames = []

	os.makedirs("output", exist_ok=True)
	os.makedirs("output/difference", exist_ok=True)

	for frame, time in iter_frame_time(scene.duration, scene.frame_rate, inclusive=True):
		filename = "output/frame_%04d.png" % frame
		print("Rendering:", os.path.basename(filename))

		"""
		r1tl.update_animations(time)
		r1tr.update_animations(time)
		r1bl.update_animations(time)
		r1br.update_animations(time)

		r2.update_animations(time)
		"""

		t1.update_animations(time)

		frame = renderer.render(scene)
		frame.save(filename)

		frames.append(frame)

	_save_gif("output.gif", frames, scene.frame_rate)

	"""
	frame_differences = []

	for i, (frame_before, frame_after) in enumerate(pairwise(frames)):
		diff = _render_difference(frame_before, frame_after)
		diff.save("output/difference/frame_%04d_%04d.png" % (i, i + 1))

		frame_differences.append(diff)

	_save_gif("output_difference.gif", frame_differences, scene.frame_rate)
	"""
