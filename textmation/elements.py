#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import attrgetter
from math import ceil

from .descriptors import *
from .properties import *
from .animation import Animation
from .utilities import setattr_consecutive


class Element:
	def __init__(self, children=None):
		if children is None:
			children = ()
		self.children = list(children)
		self.parent = None
		for child in self.children:
			child.parent = self
		self.animations = set()

	def add(self, element):
		assert element is not None
		if isinstance(element, Animation):
			self.animations.add(element)
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
		value = animation.get_value(time)
		setattr_consecutive(self, animation.property, value)

	def update_animations(self, time):
		for animation in self.animations:
			self.apply_animation(animation, time)

	def update(self, time):
		for element in self.traverse():
			element.update_animations(time)


class Scene(Element):
	size = TypedProperty(Size)
	background = TypedProperty(Color)
	frame_rate = Positive()

	def __init__(self, size=None, background=None):
		super().__init__()
		if size is None:
			size = Size()
		if background is None:
			background = Color()
		assert isinstance(size, Size)
		assert isinstance(background, Color)
		self.size = size
		self.background = background
		self.frame_rate = 20
		self._duration = None

	@property
	def duration(self):
		if self._duration is not None:
			return self._duration
		return ceil(max(map(attrgetter("end_time"), self.traverse_animations()), default=0))

	@duration.setter
	def duration(self, duration):
		self._duration = duration


class Rectangle(Element):
	bounds = TypedProperty(Rect)
	color = TypedProperty(Color)

	def __init__(self, bounds=None, color=None):
		super().__init__()
		if bounds is None:
			bounds = Rect()
		if color is None:
			color = Color()
		assert isinstance(bounds, Rect)
		assert isinstance(color, Color)
		self.bounds = bounds
		self.color = color


class Text(Element):
	text = StringProperty()
	font = StringProperty()
	font_size = Positive()
	color = TypedProperty(Color)
	bounds = TypedProperty(Rect)

	def __init__(self, text=None, position=None):
		super().__init__()
		if text is None:
			text = ""
		if position is None:
			position = Point()
		assert isinstance(text, str)
		assert isinstance(position, Point)
		self.text = text
		self.font = "arial"
		self.font_size = 32
		self.color = Color(255, 255, 255)
		self.position = position
