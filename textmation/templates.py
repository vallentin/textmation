#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps

from .datatypes import *
from .element import Element, Percentage


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
		return Template.__subclasses__()

	@classmethod
	@apply_template
	def apply(cls, element: Element):
		element.define("type", cls.__name__)

		# if element._parent is not None:
		# 	element.define("parent", element._parent)


class Scene(Template):
	@classmethod
	@apply_template
	def apply(cls, element: Element):
		super().apply(element)

		element.define("width", 100, Number)
		element.define("height", 100, Number)


class Rectangle(Template):
	@classmethod
	@apply_template
	def apply(cls, element: Element):
		super().apply(element)

		element.define("x", 0, relative="width")
		element.define("y", 0, relative="height")
		element.define("width", Percentage(100), relative="width")
		element.define("height", Percentage(100), relative="height")

		element.define("fill", Vec4(255, 255, 255), Vec4)
		element.define("outline", Vec4(255, 255, 255), Vec4)
		element.define("outline_width", 1)
