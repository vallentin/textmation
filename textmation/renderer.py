#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .elements import Element, Scene
from .rasterizer import Image, Font


def iter_frame_time(duration, frame_rate, *, inclusive=False):
	frames = duration * frame_rate
	if inclusive:
		frames += 1

	for frame in range(frames):
		time = frame / frame_rate
		yield frame, time


class Renderer:
	def __init__(self):
		self._image = None
		pass

	def render(self, element):
		assert isinstance(element, Scene)
		image = self._render(element)
		assert isinstance(image, Image)
		return image

	def _render(self, element):
		assert isinstance(element, Element)
		method = "_render_%s" % element.__class__.__name__
		visitor = getattr(self, method)
		return visitor(element)

	def _render_children(self, element):
		for child in element.children:
			self._render(child)

	def _render_Scene(self, scene):
		self._image = Image.new(scene.size, scene.background)
		self._render_children(scene)
		return self._image

	def _render_Rectangle(self, rect):
		self._image.draw_rect(rect.bounds, rect.color, rect.outline_color, rect.outline_width)
		self._render_children(rect)

	def _render_Text(self, text):
		font = Font.load(text.font, text.font_size)
		self._image.draw_text(text.text, text.position, text.color, font)
		self._render_children(text)


def _render(renderer, scene, time):
	scene.update(time)
	return renderer.render(scene)


def render(scene, time=0):
	return _render(Renderer(), scene, time)


def render_animation(scene, *, inclusive=True):
	renderer = Renderer()

	frames = []
	for frame, time in iter_frame_time(scene.duration, scene.frame_rate, inclusive=inclusive):
		print(f"Rendering Frame {frame:04d}")
		frames.append(_render(renderer, scene, time))

	return frames
