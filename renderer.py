#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw

from scene import *


class Frame:
	def __init__(self, size, background=(0, 0, 0)):
		self.size = size
		self.background = background

	def save(self, filename):
		raise NotImplementedError

	def draw_rect(self, bounds, color):
		raise NotImplementedError


class Renderer:
	def __init__(self):
		self.frames = []

	@property
	def _frame(self):
		return self.frames[-1]

	def _create_frame(self, size, background):
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


class PILFrame(Frame):
	def __init__(self, size, background=(0, 0, 0)):
		super().__init__(size, background)
		self.image = Image.new("RGBA", size, background)
		self.draw = ImageDraw.Draw(self.image, "RGBA")

	def save(self, filename):
		self.image.save(filename)

	def draw_rect(self, bounds, color):
		x, y = bounds[:2]
		x2, y2 = map(sum, zip(bounds, bounds[2:]))
		self.draw.rectangle((x, y, x2, y2), fill=color)


class PILRenderer(Renderer):
	def _create_frame(self, size, background):
		return PILFrame(size, background)


if __name__ == "__main__":
	scene = Scene((200, 200))

	r1tl = Rectangle((10, 10, 85, 85), color=(255, 0, 0))
	r1tr = Rectangle((105, 10, 85, 85), color=(0, 255, 0))
	r1bl = Rectangle((10, 105, 85, 85), color=(0, 0, 255))
	r1br = Rectangle((105, 105, 85, 85), color=(255, 0, 255))

	scene.add_all((r1tl, r1tr, r1bl, r1br))

	renderer = PILRenderer()
	frame = renderer.render(scene)
	frame.save("test.png")
