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


class Scene(Element):
	# size = TypedProperty(Size)
	# background = TypedProperty(Color)
	# frame_rate = Positive()

	def __init__(self, size=None, background=None):
		super().__init__()

		if size is None:
			size = Size()
		if background is None:
			background = Color()

		assert isinstance(size, Size)
		assert isinstance(background, Color)

		self.set("size", size)
		self.set("background", background)
		self.set("frame_rate", 20)
		self.set("duration", None)

	def reset(self):
		super().reset()
		self.update_duration()

	def update_duration(self):
		duration = self.get("duration").get()
		if duration is None:
			duration = ceil(max(map(attrgetter("end_time"), self.traverse_animations()), default=0))
		self.set("duration", duration)

	@property
	def size(self):
		return self.get("size").get()

	@size.setter
	def size(self, size):
		self.set("size", size)

	@property
	def background(self):
		return self.get("background").get()

	@background.setter
	def background(self, background):
		self.set("background", background)

	@property
	def frame_rate(self):
		return self.get("frame_rate").get()

	@frame_rate.setter
	def frame_rate(self, frame_rate):
		self.set("frame_rate", frame_rate)

	@property
	def duration(self):
		return self.get("duration").get()

	@duration.setter
	def duration(self, duration):
		self.set("duration", duration)


class Group(Element):
	position = TypedProperty(Point)

	def __init__(self, position=None):
		super().__init__()

		if position is None:
			position = Point()

		self.position = position


class Rectangle(Element):
	# bounds = TypedProperty(Rect)
	# color = TypedProperty(Color)
	# outline_color = TypedProperty(Color)
	# outline_width = NonNegative()

	def __init__(self, bounds=None, color=None, outline_color=None, outline_width=1):
		super().__init__()

		if bounds is None:
			bounds = Rect()
		if color is None:
			color = Color()
		if outline_color is None:
			outline_color = Color(0, 0, 0, 0)

		assert isinstance(bounds, Rect)
		assert isinstance(color, Color)
		assert isinstance(outline_color, Color)

		self.set("x", bounds.position.x)
		self.set("y", bounds.position.y)
		self.set("width", bounds.size.width)
		self.set("height", bounds.size.height)

		self.set("color.red", color.red)
		self.set("color.green", color.green)
		self.set("color.blue", color.blue)
		self.set("color.alpha", color.alpha)

		self.set("outline_color.red", outline_color.red)
		self.set("outline_color.green", outline_color.green)
		self.set("outline_color.blue", outline_color.blue)
		self.set("outline_color.alpha", outline_color.alpha)

		self.set("outline_width", outline_width)

	@property
	def bounds(self):
		return Rect(
			Point(
				self.get_computed("x").get(),
				self.get_computed("y").get()),
			Size(
				self.get_computed("width").get(),
				self.get_computed("height").get()))

	@property
	def color(self):
		return Color(
			self.get_computed("color.red").get(),
			self.get_computed("color.green").get(),
			self.get_computed("color.blue").get(),
			self.get_computed("color.alpha").get())

	@property
	def outline_color(self):
		return Color(
			self.get_computed("outline_color.red").get(),
			self.get_computed("outline_color.green").get(),
			self.get_computed("outline_color.blue").get(),
			self.get_computed("outline_color.alpha").get())

	@property
	def outline_width(self):
		return self.get_computed("outline_width").get()


class Circle(Element):
	center = TypedProperty(Point)
	radius = NonNegative()
	color = TypedProperty(Color)
	outline_color = TypedProperty(Color)
	outline_width = NonNegative()

	def __init__(self, center=None, radius=1, color=None, outline_color=None, outline_width=1):
		super().__init__()

		if center is None:
			center = Point()
		if color is None:
			color = Color()
		if outline_color is None:
			outline_color = Color(0, 0, 0, 0)

		assert isinstance(center, Point)
		assert isinstance(color, Color)
		assert isinstance(outline_color, Color)

		self.center = center
		self.radius = radius
		self.color = color
		self.outline_color = outline_color
		self.outline_width = outline_width


class Ellipse(Element):
	center = TypedProperty(Point)
	radius_x = NonNegative()
	radius_y = NonNegative()
	color = TypedProperty(Color)
	outline_color = TypedProperty(Color)
	outline_width = NonNegative()

	def __init__(self, center=None, radius_x=1, radius_y=None, color=None, outline_color=None, outline_width=1):
		super().__init__()

		if center is None:
			center = Point()
		if color is None:
			color = Color()
		if outline_color is None:
			outline_color = Color(0, 0, 0, 0)

		assert isinstance(center, Point)
		assert isinstance(color, Color)
		assert isinstance(outline_color, Color)

		self.center = center
		self.radius_x = radius_x
		self.radius_y = radius_y
		self.color = color
		self.outline_color = outline_color
		self.outline_width = outline_width


class Line(Element):
	p1 = TypedProperty(Point)
	p2 = TypedProperty(Point)
	width = NonNegative()
	color = TypedProperty(Color)

	def __init__(self, p1=None, p2=None, color=None, width=1):
		super().__init__()

		if p1 is None:
			p1 = Point()
		if p2 is None:
			p2 = Point()
		if color is None:
			color = Color()

		assert isinstance(p1, Point)
		assert isinstance(p2, Point)
		assert isinstance(color, Color)

		self.p1 = p1
		self.p2 = p2
		self.width = width
		self.color = color


class Text(Element):
	text = StringProperty()
	font = StringProperty()
	font_size = Positive()
	anchor = TypedProperty(Anchor)
	alignment = TypedProperty(Alignment)
	position = TypedProperty(Point)
	color = TypedProperty(Color)

	def __init__(self, text=None, position=None, anchor=Anchor.Center, alignment=Alignment.Left):
		super().__init__()

		if text is None:
			text = ""
		if position is None:
			position = Point()

		assert isinstance(text, str)
		assert isinstance(position, Point)
		assert isinstance(alignment, Alignment)

		self.text = text
		self.font = "arial"
		self.font_size = 32
		self.anchor = anchor
		self.alignment = alignment
		self.position = position
		self.color = Color(255, 255, 255)
