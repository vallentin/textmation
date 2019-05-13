#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager, redirect_stdout
from operator import itemgetter
from math import ceil
from io import StringIO
import sys

from .datatypes import Point
from .rasterizer import Image, load_image, load_font, to_color
from .elements import Element, Scene, ImageFit, TextAnchor, TextAlignment
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
			method = f"_render_{element.__class__.__name__}"
			visitor = getattr(self, method)
		except AttributeError:
			for cls in filter(lambda cls: issubclass(cls, Element), iter_all_superclasses(element.__class__)):
				try:
					method = f"_render_{cls.__name__}"
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
		self._image = Image(max(int(scene.p_width), 0), max(int(scene.p_height), 0), to_color(scene.p_background))
		self._render_children(scene)
		return self._image

	def _render_Drawable(self, drawable):
		with self.translate(Point(drawable.p_x, drawable.p_y)):
			self._render_children(drawable)

	# def _render_Group(self, group):
	# 	with self.translate(group.position):
	# 		self._render_children(group)

	def _render_Rectangle(self, rect):
		tx, ty = self.translation
		lx, ly = rect.p_x, rect.p_y
		x, y = round(lx + tx), round(ly + ty)
		w, h = max(round(rect.p_width), 0), max(round(rect.p_height), 0)

		self._image.draw_rect((x, y, w, h), to_color(rect.p_fill))

		# TODO: rect.p_outline, rect.p_outline_width

		with self.translate(Point(lx, ly)):
			self._render_children(rect)

	def _render_Line(self, line):
		tx, ty = self.translation
		x1, y1 = round(line.p_x1 + tx), round(line.p_y1 + ty)
		x2, y2 = round(line.p_x2 + tx), round(line.p_y2 + ty)

		self._image.draw_line((x1, y1), (x2, y2), to_color(line.p_fill))

		# TODO: line.p_width

		# TODO: Translate to p1, p2, min(p1, p2) or at all?
		self._render_children(line)

	def _render_Circle(self, circle):
		tx, ty = self.translation
		cx, cy = round(circle.p_center_x + tx), round(circle.p_center_y + ty)

		r = max(round(circle.p_radius), 0)

		self._image.draw_circle((cx, cy), r, to_color(circle.p_fill))

		# TODO: circle.p_outline, circle.p_outline_width

		# TODO: Translate to min or center?
		self._render_children(circle)

	def _render_Ellipse(self, ellipse):
		tx, ty = self.translation
		cx, cy = round(ellipse.p_center_x + tx), round(ellipse.p_center_y + ty)

		rx, ry = ellipse.p_radius_x, ellipse.p_radius_y
		rx, ry = max(round(rx), 0), max(round(ry), 0)

		self._image.draw_ellipse((cx, cy), (rx, ry), to_color(ellipse.p_fill))

		# TODO: ellipse.p_outline, ellipse.p_outline_width

		# TODO: Translate to min or center?
		self._render_children(ellipse)

	def _render_Arc(self, arc):
		raise NotImplementedError
		# center = Point(arc.p_center_x, arc.p_center_y)
		# if arc.p_start_angle == 0 and arc.p_end_angle == 360:
		# 	self._image.draw_ellipse(self.translation + center, arc.p_radius_x, arc.p_radius_y, arc.p_color, arc.p_outline, arc.p_outline_width)
		# else:
		# 	self._image.draw_arc(self.translation + center, arc.p_radius_x, arc.p_radius_y, arc.p_fill, arc.p_outline, arc.p_outline_width, arc.p_start_angle.degrees, arc.p_end_angle.degrees)
		# self._render_children(arc)

	def _render_Image(self, image):
		_image = load_image(image.p_filename)

		tx, ty = self.translation
		lx, ly = image.p_x, image.p_y
		x, y = round(lx + tx), round(ly + ty)
		w, h = max(round(image.p_width), 0), max(round(image.p_height), 0)

		fit = image.p_fit

		if fit in (ImageFit.Contain, ImageFit.Cover):
			img_w, img_h = _image.size()

			sx = w / img_w
			sy = h / img_h

			if fit == ImageFit.Contain:
				scale = min(sx, sy)

				if sx > sy:
					x += (w / 2) - (img_w / 2 * sy)
				else:
					y += (h / 2) - (img_h / 2 * sx)
			else: # elif fit == ImageFit.Cover:
				scale = max(sx, sy)

				if sx < sy:
					x += (w / 2) - (img_w / 2 * sy)
				else:
					y += (h / 2) - (img_h / 2 * sx)

			w = img_w * scale
			h = img_h * scale
		# else: # elif fit == ImageFit.Fill:
		# 	pass

		self._image.draw_image((x, y, w, h), _image)

		with self.translate(Point(lx, ly)):
			self._render_children(image)

	def _render_Text(self, text):
		font = load_font(text.p_font)
		font_size = text.p_font_size

		tx, ty = self.translation
		x, y = round(text.p_x + tx), round(text.p_y + ty)

		_text = text.p_text
		is_multiline = "\n" in _text

		if is_multiline:
			lines = text.p_text.splitlines()
			sizes = []

			for line in lines:
				sizes.append(font.measure_line(line, font_size))

			text_width = max(map(itemgetter(0), sizes))
			text_height = sum(map(itemgetter(1), sizes))
		else:
			text_width, text_height = font.measure_line(_text, font_size)

		anchor = text.p_anchor

		if anchor & TextAnchor.CenterX:
			x -= text_width / 2
		elif anchor & TextAnchor.Right:
			x -= text_width
		# elif anchor & TextAnchor.Left:
		# 	pass

		if anchor & TextAnchor.CenterY:
			y -= text_height / 2
		elif anchor & TextAnchor.Bottom:
			y -= text_height
		# elif anchor & TextAnchor.Top:
		# 	pass

		fill = to_color(text.p_fill)

		if is_multiline:
			alignment = text.p_alignment

			for line, (line_w, line_h) in zip(lines, sizes):
				line_x = x

				if alignment == TextAlignment.Left:
					pass
				elif alignment == TextAlignment.Center:
					line_x += (text_width / 2) - (line_w / 2)
				elif alignment == TextAlignment.Right:
					line_x += text_width - line_w

				self._image.draw_text((line_x, y), line, font, font_size, fill)
				y += line_h
		else:
			self._image.draw_text((x, y), _text, font, font_size, fill)

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
