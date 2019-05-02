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

	def contains(self, other):
		(left, top), (right, bottom) = self.min, self.max

		if isinstance(other, Rect):
			(left2, top2), (right2, bottom2) = other.min, other.max
			return (left <= left2) and \
			       (right >= right2) and \
			       (top <= top2) and \
			       (bottom >= bottom2)
		elif isinstance(other, (Vec2, Point)):
			x, y = other
			# return (left >= x) and \
			#        (right <= x) and \
			#        (bottom >= y) and \
			#        (top <= y)
			return left <= x <= right and top <= y <= bottom
		else:
			raise NotImplementedError

	def intersects(self, other):
		assert isinstance(other, Rect)

		(left1, top1), (right1, bottom1) = self.min, self.max
		(left2, top2), (right2, bottom2) = other.min, other.max

		# return (left1 <= right2) and \
		#        (left2 <= right1) and \
		#        (top1 <= bottom2) and \
		#        (top2 <= bottom1)

		return (left1 < right2) and \
		       (left2 < right1) and \
		       (top1 < bottom2) and \
		       (top2 < bottom1)

	def intersected(self, other):
		assert isinstance(other, Rect)

		(left1, top1), (right1, bottom1) = self.min, self.max
		(left2, top2), (right2, bottom2) = other.min, other.max

		x1, y1 = max(left1, left2), max(top1, top2)
		x2, y2 = min(right1, right2), min(bottom1, bottom2)
		w, h = x2 - x1, y2 - y1

		return Rect(x1, y1, w, h)

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
		if isinstance(other, Vec2):
			return Rect(other - self.position, self.size)
		if isinstance(other, Number):
			return Rect(other - self.position, self.size)
		if isinstance(other, (int, float)):
			return Vec2(other) - self
		return NotImplemented

	def __eq__(self, other):
		if isinstance(other, Rect):
			return self.position == other.position and \
			       self.size == other.size
		return NotImplemented

	def __repr__(self):
		return f"{self.__class__.__name__}({self.position!r}, {self.size!r})"
