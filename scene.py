#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Element:
	def __init__(self, children=None):
		if children is None:
			children = ()
		self.children = list(children)
		self.parent = None
		for child in self.children:
			child.parent = self

	def add(self, element):
		assert element.parent is None
		element.parent = self
		self.children.append(element)

	def add_all(self, elements):
		for element in elements:
			self.add(element)


class Scene(Element):
	def __init__(self, size, background=(0, 0, 0), children=None):
		super().__init__(children)
		self.size = size
		self.background = background


class Rectangle(Element):
	def __init__(self, bounds, color, children=None):
		super().__init__(children)
		self.bounds = bounds
		self.color = color
