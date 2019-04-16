#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import attrgetter
from math import ceil

from .descriptors import *
from .properties import *
from .animation import AnimationFillMode, Infinite, Animation
from .rasterizer import Anchor, Alignment
from .utilities import setattr_consecutive


class ElementProperty:
	def __init__(self, element, name, value=None):
		self.element = element
		self.name = name
		self.value = value

	def get(self):
		return self.value

	def set(self, value):
		assert not isinstance(value, (ElementProperty, ElementProperties))
		self.value = value
		return self

	def __repr__(self):
		if self.value is None:
			return f"{self.__class__.__name__}({self.element.__class__.__name__}, {self.name!r})"
		else:
			return f"{self.__class__.__name__}({self.element.__class__.__name__}, {self.name!r}, {self.value!r})"


class ElementProperties:
	def __init__(self, element):
		self.element = element
		self.properties = {}

	def __getitem__(self, name):
		try:
			return self.properties[name]
		except KeyError:
			property = ElementProperty(self.element, name)
			self.properties[name] = property
			return property

	def items(self):
		return self.properties.items()


class Element:
	def __init__(self, children=None):
		self.name = None

		self.properties = ElementProperties(self)
		self.computed_properties = ElementProperties(self)

		if children is None:
			children = ()

		self.children = list(children)
		self.parent = None

		for child in self.children:
			child.parent = self

		self.animations = []

	def apply(self, element):
		if self.name is not None:
			element.name = self.name
		else:
			element.name = self.__class__.__name__

		for name, value in self.properties.items():
			element.set(name, value.get())

		for child in self.children:
			element.add(child.copy())

		for animation in self.animations:
			element.add(animation)

		return element

	def copy(self):
		element = Element()
		self.apply(element)
		return element

	def add(self, element):
		assert element is not None
		if isinstance(element, Animation):
			assert element not in self.animations
			self.animations.append(element)
		else:
			assert isinstance(element, Element)
			assert element.parent is None
			element.parent = self
			self.children.append(element)

	def add_all(self, elements):
		for element in elements:
			self.add(element)

	def traverse(self):
		yield self
		for child in self.children:
			yield from child.traverse()

	def traverse_animations(self):
		for element in self.traverse():
			yield from element.animations

	def apply_animation(self, animation, time):
		if not animation.is_affecting(time):
			return

		value = animation.get_value(time)

		# TODO: setattr_consecutive(self, animation.property, value)
		# assert "." not in animation.property

		computed_property = self.get_computed(animation.property)
		current_value = computed_property.get()
		current_value = animation.composite_func(current_value, value)
		computed_property.set(current_value)

	def update_animations(self, time):
		for animation in self.animations:
			self.apply_animation(animation, time)

	# def update(self, time):
	# 	for element in self.traverse():
	# 		element.update_animations(time)

	def get(self, name):
		return self.properties[name]

	def set(self, name, value):
		return self.get(name).set(value)

	def get_computed(self, name):
		return self.computed_properties[name]

	def reset(self):
		self.reset_children()

	def reset_children(self):
		for child in self.children:
			child.reset()

	def compute(self, time):
		for name, value in self.properties.items():
			self.get_computed(name).set(value.get())
		self.update_animations(time)
		self.compute_children(time)

	def compute_children(self, time):
		for child in self.children:
			child.compute(time)
