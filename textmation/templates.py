#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps

from .datatypes import *
from .element import Element, Percentage
from .utilities import iter_all_subclasses


def apply_template(f):
	@wraps(f)
	def wrapper(cls, element):
		assert isinstance(element, Element)
		f(cls, element)
		return element
	return wrapper


class Template:
	@staticmethod
	def list_templates():
		return list(iter_all_subclasses(Template))

	@classmethod
	def super(cls):
		assert len(cls.__bases__) == 1
		template = cls.__bases__[0]
		if issubclass(template, Template):
			return template
		return None

	@classmethod
	@apply_template
	def apply(cls, element: Element):
		element.define("type", cls.__name__)

		# TODO: Currently it's possible to do
		# TODO: parent = parent.parent
		# TODO: This will be resolved when readonly properties are added
		if element._parent is not None:
			element.define("parent", element._parent)


class Scene(Template):
	@classmethod
	@apply_template
	def apply(cls, element: Element):
		super().apply(element)

		element.define("width", 100, Number)
		element.define("height", 100, Number)

		# TODO: alias size <-> width, height

		element.define("background", Vec4(0, 0, 0, 255))
		# TODO: alias background <-> fill

		element.define("frame_rate", 20, Number)

		# TODO: Calculate total duration by default
		element.define("duration", 1, Number)

		# TODO: Remove?
		# TODO: element.define("frames", 1, Number)

		# TODO: What should the default be?
		element.define("inclusive", 1, Number)


class Drawable(Template):
	@classmethod
	@apply_template
	def apply(cls, element: Element):
		super().apply(element)

		element.define("x", 0, relative="width")
		element.define("y", 0, relative="height")
		element.define("width", Percentage(100), relative="width")
		element.define("height", Percentage(100), relative="height")


class Rectangle(Drawable):
	@classmethod
	@apply_template
	def apply(cls, element: Element):
		super().apply(element)

		element.define("color", Vec4(255, 255, 255, 255))
		element.define("fill", element.get("color"))

		element.define("outline", Vec4(0, 0, 0, 0), Vec4)
		element.define("outline_width", 1)


class Circle(Drawable):
	@classmethod
	@apply_template
	def apply(cls, element: Element):
		super().apply(element)

		element.define("center_x", BinOp("+", Percentage(50), BinOp("/", element.get("width"), Number(2))), relative="width")
		element.define("center_y", BinOp("+", Percentage(50), BinOp("/", element.get("height"), Number(2))), relative="height")

		# TODO: Should radius be relative to width, height, min(width, height) or max(width, height)
		# element.define("radius", Percentage(50), relative="width")
		element.define("diameter", Percentage(100), relative="width")
		element.define("radius", BinOp("/", element.get("diameter"), Number(2)), relative="width")

		# element.set("x", BinOp("-", element.get("center_x"), element.get("radius")))
		element.set("x", BinOp("-", element.get("center_x"), BinOp("/", element.get("width"), Number(2))))

		# element.set("y", BinOp("-", element.get("center_y"), element.get("radius")))
		element.set("y", BinOp("-", element.get("center_y"), BinOp("/", element.get("height"), Number(2))))

		element.set("width", BinOp("*", element.get("radius"), Number(2)))
		element.set("height", BinOp("*", element.get("radius"), Number(2)))

		element.define("color", Vec4(255, 255, 255, 255))
		element.define("fill", element.get("color"))

		element.define("outline", Vec4(0, 0, 0, 0), Vec4)
		element.define("outline_width", 1)


class Ellipse(Drawable):
	@classmethod
	@apply_template
	def apply(cls, element: Element):
		super().apply(element)

		element.define("center_x", BinOp("+", Percentage(50), BinOp("/", element.get("width"), Number(2))), relative="width")
		element.define("center_y", BinOp("+", Percentage(50), BinOp("/", element.get("height"), Number(2))), relative="height")

		# TODO: Should radius be relative to width, height, min(width, height) or max(width, height)
		# element.define("radius", Percentage(50), relative="width")
		element.define("diameter", Percentage(100), relative="width")
		element.define("radius", BinOp("/", element.get("diameter"), Number(2)), relative="width")

		element.define("diameter_x", element.get("diameter"), relative="width")
		element.define("diameter_y", element.get("diameter"), relative="height")
		element.define("radius_x", BinOp("/", element.get("diameter_x"), Number(2)), relative="width")
		element.define("radius_y", BinOp("/", element.get("diameter_y"), Number(2)), relative="height")

		# element.set("x", BinOp("-", element.get("center_x"), element.get("radius_x")))
		element.set("x", BinOp("-", element.get("center_x"), BinOp("/", element.get("width"), Number(2))))

		# element.set("y", BinOp("-", element.get("center_y"), element.get("radius_y")))
		element.set("y", BinOp("-", element.get("center_y"), BinOp("/", element.get("height"), Number(2))))

		element.set("width", BinOp("*", element.get("radius_x"), Number(2)))
		element.set("height", BinOp("*", element.get("radius_y"), Number(2)))

		element.define("color", Vec4(255, 255, 255, 255))
		element.define("fill", element.get("color"))

		element.define("outline", Vec4(0, 0, 0, 0), Vec4)
		element.define("outline_width", 1)


class Line(Drawable):
	@classmethod
	@apply_template
	def apply(cls, element: Element):
		super().apply(element)

		element.define("x1", 0, relative="width")
		element.define("y1", 0, relative="height")

		element.define("x2", 0, relative="width")
		element.define("y2", 0, relative="height")

		element.set("x", element.get("x1"))
		element.set("y", element.get("y1"))

		element.define("color", Vec4(255, 255, 255, 255))
		element.define("fill", element.get("color"))

		# TODO: Intersects with Drawable's width
		# element.define("width", 1)
		element.set("width", 1)


class Text(Drawable):
	@classmethod
	@apply_template
	def apply(cls, element: Element):
		super().apply(element)

		element.define("text", "")

		element.define("font", "arial")
		element.define("font_size", 32)

		# TODO: Use enums and add type checking
		element.define("anchor", "Center")
		element.define("alignment", "Left")

		element.define("color", Vec4(255, 255, 255, 255))
		element.define("fill", element.get("color"))
