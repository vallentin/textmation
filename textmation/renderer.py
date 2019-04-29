#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager, redirect_stdout
from functools import reduce
import operator
from math import ceil
from io import StringIO
import sys

from .datatypes import Point, Size, Rect
from .rasterizer import Image, Font
from .elements import Element, Scene
from .utilities import iter_all_superclasses


def calc_frame_count(duration, frame_rate, *, inclusive=False):
	frames = duration * frame_rate
	if inclusive:
		frames += 1
	frames = int(ceil(frames))
	return frames


def iter_frame_time(duration, frame_rate, *, inclusive=False):
	for frame in range(calc_frame_count(duration, frame_rate, inclusive=inclusive)):
		time = frame / frame_rate
		yield frame, time


class Renderer:
	def __init__(self):
		self._image = None
		self._translations = [Point(0, 0)]

	@property
	def translation(self):
		return self._translations[-1]

	@contextmanager
	def translate(self, offset):
		self._translations.append(self.translation + offset)
		yield self
		self._translations.pop()

	def render(self, element):
		assert isinstance(element, Element)
		assert isinstance(element, Scene)
		image = self._render(element)
		assert isinstance(image, Image)
		return image

	def _render(self, element):
		assert isinstance(element, Element)

		try:
			method = "_render_%s" % element.__class__.__name__
			visitor = getattr(self, method)
		except AttributeError:
			for cls in filter(lambda cls: issubclass(cls, Element), iter_all_superclasses(element.__class__)):
				try:
					method = "_render_%s" % cls.__name__
					visitor = getattr(self, method)
					break
				except AttributeError:
					pass
			else:
				raise

		return visitor(element)

	def _render_children(self, element):
		for child in element.elements:
			self._render(child)

	def _render_Scene(self, scene):
		self._image = Image.new(Size(scene.p_width, scene.p_height), scene.p_background)
		self._render_children(scene)
		return self._image

	def _render_Drawable(self, drawable):
		with self.translate(Point(drawable.p_x, drawable.p_y)):
			self._render_children(drawable)

	# def _render_Group(self, group):
	# 	with self.translate(group.position):
	# 		self._render_children(group)

	def _render_Rectangle(self, rect):
		bounds = Rect(rect.p_x, rect.p_y, rect.p_width, rect.p_height)
		self._image.draw_rect(bounds + self.translation, rect.p_fill, rect.p_outline, rect.p_outline_width)

		with self.translate(bounds.position):
			self._render_children(rect)

	def _render_Circle(self, circle):
		center = Point(circle.p_center_x, circle.p_center_y)
		self._image.draw_circle(self.translation + center, circle.p_radius, circle.p_fill, circle.p_outline, circle.p_outline_width)

		# TODO: Translate to min or center?
		self._render_children(circle)

	def _render_Ellipse(self, ellipse):
		center = Point(ellipse.p_center_x, ellipse.p_center_y)
		self._image.draw_ellipse(self.translation + center, ellipse.p_radius_x, ellipse.p_radius_y, ellipse.p_color, ellipse.p_outline, ellipse.p_outline_width)

		# TODO: Translate to min or center?
		self._render_children(ellipse)

	def _render_Arc(self, arc):
		center = Point(arc.p_center_x, arc.p_center_y)
		if arc.p_start_angle == 0 and arc.p_end_angle == 360:
			self._image.draw_ellipse(self.translation + center, arc.p_radius_x, arc.p_radius_y, arc.p_color, arc.p_outline, arc.p_outline_width)
		else:
			self._image.draw_arc(self.translation + center, arc.p_radius_x, arc.p_radius_y, arc.p_fill, arc.p_outline, arc.p_outline_width, arc.p_start_angle.degrees, arc.p_end_angle.degrees)
		self._render_children(arc)

	def _render_Line(self, line):
		p1, p2 = Point(line.p_x1, line.p_y1), Point(line.p_x2, line.p_y2)

		self._image.draw_line(self.translation + p1, self.translation + p2, line.p_fill, line.p_width)

		# TODO: Translate to p1, p2, min(p1, p2) or at all?
		self._render_children(line)

	def _render_Text(self, text):
		font = Font.load(text.p_font, text.p_font_size)
		position = Point(text.p_x, text.p_y)

		self._image.draw_text(text.p_text, self.translation + position, text.p_fill, font, text.p_anchor, text.p_alignment)

		# TODO: Translate?
		self._render_children(text)


def _render(renderer, scene, time):
	scene.compute(time)
	return renderer.render(scene)


def render(scene, time=0):
	return _render(Renderer(), scene, time)


# TODO: Consider removing "inclusive" and instead use "scene.p_inclusive"
def render_animation(scene, *, inclusive=True):
	renderer = Renderer()

	duration = scene.p_duration.seconds
	frame_rate = scene.p_frame_rate

	frame_count = calc_frame_count(duration, frame_rate, inclusive=inclusive)

	add_newline = False

	frames = []
	for frame, time in iter_frame_time(duration, frame_rate, inclusive=inclusive):
		# print(f"\rRendering Frame {frame+1:04d}/{frame_count:04d} ({(frame+1)/frame_count*100:.0f}%)")

		sys.stdout.write(f"\rRendering Frame {frame+1:04d}/{frame_count:04d} ({(frame+1)/frame_count*100:.0f}%)")
		sys.stdout.flush()

		f = StringIO()
		try:
			with redirect_stdout(f):
				frames.append(_render(renderer, scene, time))
		finally:
			output = f.getvalue()
			if output:
				sys.stdout.write("\n")
				sys.stdout.write(output)
				sys.stdout.flush()
			elif frame == (frame_count - 1):
				add_newline = True

	if add_newline:
		sys.stdout.write("\n")

	return frames
