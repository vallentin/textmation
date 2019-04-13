#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
from .binding import Binding


class Type(Binding):
	@staticmethod
	def check(value):
		pass

	def __init__(self, value):
		self.value = value

	def eval(self, property):
		return self.value

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.value}>"


class String(Type):
	@staticmethod
	def check(value):
		assert isinstance(value, str)


class Number(Type):
	@staticmethod
	def check(value):
		assert isinstance(value, (int, float))


class Percentage(Type):
	def eval(self, property):
		return self.value * (property.relative.eval() / 100)
"""


class Type:
	def __repr__(self):
		name = self.__class__.__name__.strip("_")
		return f"<Type: {name}>"

	__str__ = __repr__


class Value:
	def eval(self):
		return self


class _Number(Type):
	def __add__(self, other):
		if other is NumberType:
			return NumberType
		return NotImplemented

	__radd__ = __add__
	__sub__ = __add__
	__rsub__ = __add__
	__mul__ = __add__
	__rmul__ = __add__
	__truediv__ = __add__
	__rtruediv__ = __add__
	__floordiv__ = __add__
	__rfloordiv__ = __add__

	def __neg__(self):
		return NumberType


NumberType = _Number()


class Number(Value):
	type = NumberType

	def __init__(self, value):
		self.value = value

	def __add__(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value)
		return NotImplemented

	__radd__ = __add__

	def __sub__(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value)
		return NotImplemented

	def __rsub__(self, other):
		if isinstance(other, Number):
			return Number(other.value - self.value)
		return NotImplemented

	def __mul__(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value)
		return NotImplemented

	def __rmul__(self, other):
		if isinstance(other, Number):
			return Number(other.value * self.value)
		return NotImplemented

	def __truediv__(self, other):
		if isinstance(other, Number):
			return Number(self.value / other.value)
		return NotImplemented

	def __rtruediv__(self, other):
		if isinstance(other, Number):
			return Number(other.value / self.value)
		return NotImplemented

	def __neg__(self):
		return Number(-self.value)

	def __str__(self):
		return str(self.value)

	def __repr__(self):
		return f"{self.__class__.__name__}({self.value})"


class _String(Type):
	def __add__(self, other):
		return StringType

	__radd__ = __add__


StringType = _String()


class String(Value):
	type = StringType

	def __init__(self, string):
		self.string = string

	def __add__(self, other):
		return String(self.string + str(other))

	def __radd__(self, other):
		return String(str(other) + self.string)

	def __str__(self):
		return self.string

	def __repr__(self):
		return f"{self.__class__.__name__}({self.string!r})"
