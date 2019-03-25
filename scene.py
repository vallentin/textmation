#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import islice, repeat, starmap
from functools import reduce, total_ordering
from operator import attrgetter
import bisect
from math import ceil


_sentinel = object()


def normalize(value, lower, upper):
	return (value - lower) / (upper - lower)


def lerp(a, b, t):
	# return a + t * (b - a) # Imprecise
	return (1 - t) * a + t * b # Precise


def remap(value, lower1, upper1, lower2, upper2):
	# return lower2 + (upper2 - lower2) * ((value - lower1) / (upper1 - lower1))
	return lerp(lower2, upper2, normalize(value, lower1, upper1))


def lerp_tuple(a, b, t):
	try:
		return lerp(a, b, t)
	except TypeError:
		pass

	assert isinstance(a, tuple)
	assert isinstance(b, tuple)
	assert len(a) == len(b)

	return tuple(starmap(lerp, zip(a, b, repeat(t))))


def lerp_value(a, b, t):
	try:
		return lerp_tuple(a, b, t)
	except AssertionError:
		return type(a).lerp(a, b, t)


def getattr_consecutive(obj, name, default=_sentinel):
	try:
		return reduce(getattr, name.split("."), obj)
	except AttributeError as e:
		if default is _sentinel:
			raise e from None
		return default


def setattr_consecutive(obj, name, value):
	names, name = name.rpartition(".")[0::2]
	if names:
		obj = getattr_consecutive(obj, names)
	setattr(obj, name, value)


class Bounds:
	@staticmethod
	def lerp(a, b, t):
		return Color(*map(lerp, a, b, repeat(t)))

	def __init__(self, x, y, width, height):
		self.x, self.y, self.width, self.height = x, y, width, height

	def __iter__(self):
		yield self.x
		yield self.y
		yield self.width
		yield self.height

	@property
	def x2(self):
		return self.x + self.width

	@x2.setter
	def x2(self, x2):
		self.width = max(x2 - self.x, 0)

	@property
	def y2(self):
		return self.y + self.height

	@y2.setter
	def y2(self, y2):
		self.height = max(y2 - self.y, 0)

	@property
	def min(self):
		return self.x, self.y

	@property
	def max(self):
		return self.x2, self.y2

	def __repr__(self):
		return "%s(%r, %r, %r, %r)" % (self.__class__.__name__, self.x, self.y, self.width, self.height)


class Color:
	@staticmethod
	def lerp(a, b, t):
		return Color(*map(lerp, a, b, repeat(t)))

	def __init__(self, red, green, blue, alpha=255):
		self.red, self.green, self.blue, self.alpha = red, green, blue, alpha

	def __iter__(self):
		yield self.red
		yield self.green
		yield self.blue
		yield self.alpha

	def __repr__(self):
		return "%s(%r, %r, %r, %r)" % (self.__class__.__name__, self.red, self.green, self.blue, self.alpha)


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


class Scene(Element):
	def __init__(self, size, background=(0, 0, 0), children=None):
		super().__init__(children)
		if not isinstance(background, Color):
			assert isinstance(background, tuple)
			background = Color(*background)
		self.size = size
		self.background = background
		self.frame_rate = 20
		self._duration = None

	@property
	def duration(self):
		if self._duration is not None:
			return self._duration
		return ceil(max(map(attrgetter("end_time"), self.traverse_animations())))

	@duration.setter
	def duration(self, duration):
		self._duration = duration


class Rectangle(Element):
	def __init__(self, bounds, color=(0, 0, 0), children=None):
		super().__init__(children)
		if len(bounds) == 2:
			bounds = 0, 0, *bounds
		if not isinstance(bounds, Bounds):
			assert isinstance(bounds, tuple)
			bounds = Bounds(*bounds)
		if not isinstance(color, Color):
			assert isinstance(color, tuple)
			color = Color(*color)
		self.bounds = bounds
		self.color = color

	@property
	def x(self):
		return self.bounds.x

	@x.setter
	def x(self, x):
		self.bounds.x = x

	@property
	def y(self):
		return self.bounds.y

	@y.setter
	def y(self, y):
		self.bounds.y = y

	@property
	def width(self):
		return self.bounds.width

	@width.setter
	def width(self, width):
		self.bounds.width = width

	@property
	def height(self):
		return self.bounds.height

	@height.setter
	def height(self, height):
		self.bounds.height = height


class Text(Element):
	def __init__(self, text, position=(0, 0)):
		super().__init__()
		assert isinstance(position, tuple)
		assert len(position) == 2
		self.text = text
		self.font = "arial"
		self.font_size = 10
		self.color = Color(255, 255, 255)
		self.position = position


class Animation:
	def __init__(self, property=None):
		self.keyframes = []
		self.property = property
		self.delay = 0

	@property
	def begin_time(self):
		return self.keyframes[0].time + self.delay

	@property
	def end_time(self):
		return self.keyframes[-1].time + self.delay

	@property
	def duration(self):
		return self.end_time - self.begin_time

	def add(self, keyframe):
		# self.keyframes.append(keyframe)
		# self.keyframes.sort()
		bisect.insort(self.keyframes, keyframe)

	def add_all(self, keyframes):
		for keyframe in keyframes:
			self.add(keyframe)

	def get_between(self, time):
		assert self.keyframes

		first = self.keyframes[0]
		if time < first.time:
			return first, first

		last = self.keyframes[-1]
		if time >= last.time:
			return last, last

		# index = bisect.bisect_left(self.keyframes, Keyframe(time, None))

		for i, keyframe in enumerate(islice(self.keyframes, 1, None), start=1):
			if time < keyframe.time:
				return self.keyframes[i - 1], keyframe

		assert False

	def get_value(self, time):
		time -= self.delay

		before, after = self.get_between(time)
		if before == after:
			return before.value

		# return remap(time, before.time, after.time, before.value, after.value)

		t = normalize(time, before.time, after.time)
		return lerp_value(before.value, after.value, t)


@total_ordering
class Keyframe:
	def __init__(self, time, value):
		self._time = time
		self.value = value

	@property
	def time(self):
		return self._time

	def __lt__(self, other):
		return self._time < other._time

	def __repr__(self):
		return "<%s: %.2fs, %r>" % (self.__class__.__name__, self.time, self.value)
