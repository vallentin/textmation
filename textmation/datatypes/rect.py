#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import *
from .scalars import *
from .vectors import *


class _Rect(Type):
	def __add__(self, other):
		if other in (Vec2Type, NumberType):
			return RectType
		return NotImplemented

	__radd__ = __add__
	__sub__ = __add__
	__rsub__ = __add__


RectType = _Rect()


class Point(Vec2):
	pass


class Size(Vec2):
	@property
	def width(self):
		return self.x

	@width.setter
	def width(self, width):
		self.x = width

	@property
	def height(self):
		return self.y

	@height.setter
	def height(self, height):
		self.y = height

	@property
	def area(self):
		return self.width * self.height


class Rect(Value):
	type = RectType

	def __init__(self, *rect):
		assert 0 <= len(rect) <= 2 or len(rect) == 4

		if len(rect) == 0:
			position, size = Point(), Size()
		elif len(rect) == 1:
			position, size = Point(), Size(*rect[0])
		elif len(rect) == 2:
			position, size = Point(*rect[0]), Size(*rect[1])
		else: # elif len(rect) == 4:
			position, size = Point(rect[0], rect[1]), Size(rect[2], rect[3])

		assert isinstance(position, Point)
		assert isinstance(size, Size)

		self.position, self.size = position, size

	@property
	def min(self):
		return self.position

	@property
	def max(self):
		return Point(*(self.position + self.size))

	def is_constant(self):
		return True

	def __add__(self, other):
		if isinstance(other, Vec2):
			return Rect(self.position + other, self.size)
		if isinstance(other, Number):
			return self + Vec2(other.value)
		if isinstance(other, (int, float)):
			return self + Vec2(other)
		return NotImplemented

	__radd__ = __add__

	def __sub__(self, other):
		if isinstance(other, Vec2):
			return Rect(self.position - other, self.size)
		if isinstance(other, Number):
			return self - Vec2(other.value)
		if isinstance(other, (int, float)):
			return self - Vec2(other)
		return NotImplemented

	def __rsub__(self, other):
		if isinstance(other, Number):
			return Rect(other - self.position, self.size)
		if isinstance(other, (int, float)):
			return Vec2(other) - self
		return NotImplemented

	def __repr__(self):
		return f"{self.__class__.__name__}({self.position!r}, {self.size!r})"
