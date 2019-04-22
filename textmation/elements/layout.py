#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .element import Percentage
from .drawables import Drawable


class HBox(Drawable):
	def on_element(self, element):
		super().on_element(element)

		element.define("ix", len(self.elements) - 1)

	def on_created(self):
		super().on_created()

		element_count = len(self.elements)
		for i, element in enumerate(self.elements):
			element.set("x", Percentage(i / element_count * 100))
			element.set("y", 0)
			element.set("width", Percentage(100 / element_count))
			element.set("height", Percentage(100))


class VBox(Drawable):
	def on_element(self, element):
		super().on_element(element)

		element.define("iy", len(self.elements) - 1)

	def on_created(self):
		super().on_created()

		element_count = len(self.elements)
		for i, element in enumerate(self.elements):
			element.set("x", 0)
			element.set("y", Percentage(i / element_count * 100))
			element.set("width", Percentage(100))
			element.set("height", Percentage(100 / element_count))
