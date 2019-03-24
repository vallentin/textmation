#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import attrgetter
import os

from PIL import Image, ImageDraw

from scene import *


def iter_frame_time(duration, frame_rate, *, inclusive=False):
	frames = duration * frame_rate
	if inclusive:
		frames += 1

	for frame in range(frames):
		time = frame / frame_rate
		yield frame, time


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
		self.draw.rectangle((x, y, x2, y2), fill=tuple(map(int, color)))


class PILRenderer(Renderer):
	def _create_frame(self, size, background):
		return PILFrame(size, background)


def _save_gif(filename, frames, frame_rate):
	frames = list(map(attrgetter("image"), frames))
	frames[0].save(
		filename,
		append_images=frames[1:],
		save_all=True,
		duration=1000 / frame_rate,
		loop=0,
		optimize=False)


if __name__ == "__main__":
	scene = Scene((200, 200))

	r1tl = Rectangle((10, 10, 85, 85), color=(255, 0, 0))
	r1tr = Rectangle((105, 10, 85, 85), color=(0, 255, 0))
	r1bl = Rectangle((10, 105, 85, 85), color=(0, 0, 255))
	r1br = Rectangle((105, 105, 85, 85), color=(255, 0, 255))

	scene.add_all((r1tl, r1tr, r1bl, r1br))

	a1tl = Animation("color")
	a1tl.add(Keyframe(0, (0, 0, 0)))
	a1tl.add(Keyframe(1, (255, 0, 0)))
	a1tl.add(Keyframe(2, (0, 0, 0)))

	a1tr = Animation("color")
	a1tr.delay = 0.5
	a1tr.add(Keyframe(0, (0, 0, 0)))
	a1tr.add(Keyframe(1, (0, 255, 0)))
	a1tr.add(Keyframe(2, (0, 0, 0)))

	a1bl = Animation("color")
	a1bl.delay = 1.0
	a1bl.add(Keyframe(0, (0, 0, 0)))
	a1bl.add(Keyframe(1, (0, 0, 255)))
	a1bl.add(Keyframe(2, (0, 0, 0)))

	a1br = Animation("color")
	a1br.delay = 1.5
	a1br.add(Keyframe(0, (0, 0, 0)))
	a1br.add(Keyframe(1, (255, 0, 255)))
	a1br.add(Keyframe(2, (0, 0, 0)))

	r1tl.add(a1tl)
	r1tr.add(a1tr)
	r1bl.add(a1bl)
	r1br.add(a1br)

	renderer = PILRenderer()
	frames = []

	os.makedirs("output", exist_ok=True)

	for frame, time in iter_frame_time(scene.duration, scene.frame_rate, inclusive=True):
		filename = "output/frame_%04d.png" % frame
		print("Rendering:", os.path.basename(filename))

		r1tl.update_animations(time)
		r1tr.update_animations(time)
		r1bl.update_animations(time)
		r1br.update_animations(time)

		frame = renderer.render(scene)
		frame.save(filename)

		frames.append(frame)

	_save_gif("output.gif", frames, scene.frame_rate)
