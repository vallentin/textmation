#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .descriptors import *


class Color:
	def __init__(self, red=0, green=0, blue=0, alpha=255):
		self.red, self.green, self.blue, self.alpha = red, green, blue, alpha

	def __repr__(self):
		if self.alpha == 255:
			return f"{self.__class__.__name__}({self.red!r}, {self.green!r}, {self.blue!r})"
		else:
			return f"{self.__class__.__name__}({self.red!r}, {self.green!r}, {self.blue!r}, {self.alpha!r})"


class Point:
	def __init__(self, x=0, y=None):
		if y is None:
			y = x
		self.x, self.y = x, y

	def set(self, point):
		self.x, self.y = point.x, point.y

	def __repr__(self):
		return f"{self.__class__.__name__}({self.x!r}, {self.y!r})"


class Size:
	width = NonNegative()
	height = NonNegative()

	def __init__(self, width=0, height=None):
		if height is None:
			height = width
		self.width, self.height = width, height

	def set(self, size):
		self.width, self.height = size.width, size.height

	def __repr__(self):
		return f"{self.__class__.__name__}({self.width!r}, {self.height!r})"


class Rect:
	def __init__(self, position=None, size=None):
		self._position, self._size = Point(), Size()

		if size is None and position is not None:
			size = position
			position = None

		if position is not None:
			self.position = position

		if isinstance(size, Size):
			self.size = size
		elif isinstance(size, Point):
			self.max = size

	def set(self, rect):
		self.position.set(rect.position)
		self.size.set(rect.size)

	@property
	def position(self):
		return self._position

	@position.setter
	def position(self, position):
		assert isinstance(position, Point)
		self._position.set(position)

	@property
	def size(self):
		return self._size

	@size.setter
	def size(self, size):
		assert isinstance(size, Size)
		self._size.set(size)

	min = ShorthandProperty("position")

	@property
	def max(self):
		return Point(
			self.position.x + self.size.width,
			self.position.y + self.size.height)

	@max.setter
	def max(self, max):
		self.size = Size(
			max.x - self.position.x,
			max.y - self.position.y)

	def __repr__(self):
		return f"{self.__class__.__name__}({self.position!r}, {self.size!r})"
