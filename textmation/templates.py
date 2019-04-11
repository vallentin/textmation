#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps

from .datatypes import *
from .element import Element


def apply_template(f):
	@wraps(f)
	def wrapper(cls, element):
		assert isinstance(element, Element)
		f(cls, element)
		return element
	return wrapper


class Template:
	@classmethod
	@apply_template
	def apply(cls, element: Element):
		element.define("name", cls.__name__)

		if element._parent is not None:
			element.define("parent", element._parent)


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

		element.define("x", Percentage(100), (Number, Percentage), relative=element.get("parent").eval().get("width"))
		element.define("y", Percentage(100), (Number, Percentage), relative=element.get("parent").eval().get("height"))
		element.define("width", Percentage(100), (Number, Percentage), relative=element.get("parent").eval().get("width"))
		element.define("height", Percentage(100), (Number, Percentage), relative=element.get("parent").eval().get("height"))
