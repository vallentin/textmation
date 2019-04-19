#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..datatypes import *
from .element import Element, Percentage


class BaseDrawable(Element):
	def __init__(self):
		super().__init__()
		self.elements = []

	def add(self, element):
		super().add(element)

		if isinstance(element, Drawable):
			self.elements.append(element)
		else:
			raise NotImplementedError


class Drawable(BaseDrawable):
	def on_ready(self):
		super().on_ready()

		self.define("index", self._parent._children.index(self))

		self.define("x", 0, relative="width")
		self.define("y", 0, relative="height")
		self.define("width", Percentage(100), relative="width")
		self.define("height", Percentage(100), relative="height")


class Rectangle(Drawable):
	def on_ready(self):
		super().on_ready()

		self.define("color", Vec4(255, 255, 255, 255))
		self.define("fill", self.get("color"))

		self.define("outline", Vec4(0, 0, 0, 0), Vec4)
		self.define("outline_width", 1)


class Circle(Drawable):
	def on_ready(self):
		super().on_ready()

		self.define("center_x", BinOp("+", Percentage(50), BinOp("/", self.get("width"), Number(2))), relative="width")
		self.define("center_y", BinOp("+", Percentage(50), BinOp("/", self.get("height"), Number(2))), relative="height")

		# TODO: Should radius be relative to width, height, min(width, height) or max(width, height)
		# self.define("radius", Percentage(50), relative="width")
		self.define("diameter", Percentage(100), relative="width")
		self.define("radius", BinOp("/", self.get("diameter"), Number(2)), relative="width")

		# self.set("x", BinOp("-", self.get("center_x"), self.get("radius")))
		self.set("x", BinOp("-", self.get("center_x"), BinOp("/", self.get("width"), Number(2))))

		# self.set("y", BinOp("-", self.get("center_y"), self.get("radius")))
		self.set("y", BinOp("-", self.get("center_y"), BinOp("/", self.get("height"), Number(2))))

		self.set("width", BinOp("*", self.get("radius"), Number(2)))
		self.set("height", BinOp("*", self.get("radius"), Number(2)))

		self.define("color", Vec4(255, 255, 255, 255))
		self.define("fill", self.get("color"))

		self.define("outline", Vec4(0, 0, 0, 0), Vec4)
		self.define("outline_width", 1)


class Ellipse(Drawable):
	def on_ready(self):
		super().on_ready()

		self.define("center_x", BinOp("+", Percentage(50), BinOp("/", self.get("width"), Number(2))), relative="width")
		self.define("center_y", BinOp("+", Percentage(50), BinOp("/", self.get("height"), Number(2))), relative="height")

		# TODO: Should radius be relative to width, height, min(width, height) or max(width, height)
		# self.define("radius", Percentage(50), relative="width")
		self.define("diameter", Percentage(100), relative="width")
		self.define("radius", BinOp("/", self.get("diameter"), Number(2)), relative="width")

		self.define("diameter_x", self.get("diameter"), relative="width")
		self.define("diameter_y", self.get("diameter"), relative="height")
		self.define("radius_x", BinOp("/", self.get("diameter_x"), Number(2)), relative="width")
		self.define("radius_y", BinOp("/", self.get("diameter_y"), Number(2)), relative="height")

		# self.set("x", BinOp("-", self.get("center_x"), self.get("radius_x")))
		self.set("x", BinOp("-", self.get("center_x"), BinOp("/", self.get("width"), Number(2))))

		# self.set("y", BinOp("-", self.get("center_y"), self.get("radius_y")))
		self.set("y", BinOp("-", self.get("center_y"), BinOp("/", self.get("height"), Number(2))))

		self.set("width", BinOp("*", self.get("radius_x"), Number(2)))
		self.set("height", BinOp("*", self.get("radius_y"), Number(2)))

		self.define("color", Vec4(255, 255, 255, 255))
		self.define("fill", self.get("color"))

		self.define("outline", Vec4(0, 0, 0, 0), Vec4)
		self.define("outline_width", 1)


class Line(Drawable):
	def on_ready(self):
		super().on_ready()

		self.define("x1", 0, relative="width")
		self.define("y1", 0, relative="height")

		self.define("x2", 0, relative="width")
		self.define("y2", 0, relative="height")

		self.set("x", self.get("x1"))
		self.set("y", self.get("y1"))

		self.define("color", Vec4(255, 255, 255, 255))
		self.define("fill", self.get("color"))

		# TODO: Intersects with Drawable's width
		# self.define("width", 1)
		self.set("width", 1)


class Text(Drawable):
	def on_ready(self):
		super().on_ready()

		self.define("text", "")

		self.define("font", "arial")
		self.define("font_size", 32)

		# TODO: Use enums and add type checking
		self.define("anchor", "Center")
		self.define("alignment", "Left")

		self.define("color", Vec4(255, 255, 255, 255))
		self.define("fill", self.get("color"))
