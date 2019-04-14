#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum


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
	@property
	def name(self):
		return self.__class__.__name__.strip("_")

	def __repr__(self):
		return f"<Type: {self.name}>"

	__str__ = __repr__


class Value:
	@property
	def type(self):
		raise NotImplementedError

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
		assert isinstance(value, (int, float))
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

	__rmul__ = __mul__

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
		assert isinstance(string, str)
		self.string = string

	def __add__(self, other):
		return String(self.string + str(other))

	def __radd__(self, other):
		return String(str(other) + self.string)

	def __str__(self):
		return self.string

	def __repr__(self):
		return f"{self.__class__.__name__}({self.string!r})"


class _Time(Type):
	def __add__(self, other):
		if other is TimeType:
			return TimeType
		return NotImplemented

	def __sub__(self, other):
		if other is TimeType:
			return TimeType
		return NotImplemented

	def __mul__(self, other):
		if other is NumberType:
			return TimeType
		return NotImplemented

	__rmul__ = __mul__

	def __truediv__(self, other):
		if other is NumberType:
			return TimeType
		return NotImplemented

	def __neg__(self):
		return TimeType


TimeType = _Time()


class TimeUnit(Enum):
	Seconds = "s"
	Milliseconds = "ms"


class Time(Value):
	type = TimeType

	def __init__(self, duration, unit):
		assert isinstance(duration, (int, float))
		assert isinstance(unit, TimeUnit)
		self.duration = duration
		self.unit = unit

	@property
	def seconds(self):
		if self.unit == TimeUnit.Seconds:
			return self.duration
		return self.milliseconds / 1000

	@property
	def milliseconds(self):
		if self.unit == TimeUnit.Milliseconds:
			return self.duration
		return self.seconds * 1000

	def __add__(self, other):
		if isinstance(other, Time):
			return Time(self.milliseconds + other.milliseconds, TimeUnit.Milliseconds)
		return NotImplemented

	def __sub__(self, other):
		if isinstance(other, Time):
			return Time(self.milliseconds - other.milliseconds, TimeUnit.Milliseconds)
		return NotImplemented

	def __mul__(self, other):
		if isinstance(other, Number):
			return Time(self.duration * other.value, self.unit)
		return NotImplemented

	__rmul__ = __mul__

	def __truediv__(self, other):
		if isinstance(other, Number):
			return Time(self.duration / other.value, self.unit)
		return NotImplemented

	def __neg__(self):
		return Time(-self.duration, self.unit)

	def __str__(self):
		# TODO: pprint float
		# TODO: https://stackoverflow.com/questions/2440692/formatting-floats-in-python-without-superfluous-zeros
		return f"{self.duration}{self.unit.value}"

	def __repr__(self):
		return f"{self.__class__.__name__}({self.duration!r}, {self.unit})"


class _Vec3(Type):
	def __add__(self, other):
		if other in (Vec3Type, NumberType):
			return Vec3Type
		return NotImplemented

	__radd__ = __add__
	__sub__ = __add__
	__rsub__ = __add__
	__mul__ = __add__
	__rmul__ = __add__
	__truediv__ = __add__
	__rtruediv__ = __add__


class _Vec4(Type):
	def __add__(self, other):
		if other in (Vec4Type, Vec3Type, NumberType):
			return Vec4Type
		return NotImplemented

	__radd__ = __add__
	__sub__ = __add__
	__rsub__ = __add__
	__mul__ = __add__
	__rmul__ = __add__
	__truediv__ = __add__
	__rtruediv__ = __add__


Vec3Type = _Vec3()
Vec4Type = _Vec4()


class Vec3(Value):
	type = Vec3Type

	def __init__(self, *xyz):
		assert 0 <= len(xyz) <= 3
		assert all(isinstance(x, (int, float)) for x in xyz)
		if len(xyz) == 0:
			self.x, self.y, self.z = 0, 0, 0
		elif len(xyz) == 1:
			x = xyz[0]
			self.x, self.y, self.z = x, x, x
		elif len(xyz) == 2:
			self.x, self.y, self.z = *xyz, 0
		elif len(xyz) == 3:
			self.x, self.y, self.z = xyz

	@property
	def xyz(self):
		return self.x, self.y, self.z

	def __add__(self, other):
		if isinstance(other, Vec3):
			return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
		if isinstance(other, Number):
			return self + Vec3(other.value)
		return NotImplemented

	__radd__ = __add__

	def __sub__(self, other):
		if isinstance(other, Vec3):
			return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
		if isinstance(other, Number):
			return self - Vec3(other.value)
		return NotImplemented

	def __rsub__(self, other):
		if isinstance(other, Number):
			return Vec3(other.value) - self
		return NotImplemented

	def __mul__(self, other):
		if isinstance(other, Vec3):
			return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)
		if isinstance(other, Number):
			return self * Vec3(other.value)
		return NotImplemented

	__rmul__ = __mul__

	def __truediv__(self, other):
		if isinstance(other, Vec3):
			return Vec3(self.x / other.x, self.y / other.y, self.z / other.z)
		if isinstance(other, Number):
			return self / Vec3(other.value)
		return NotImplemented

	def __rtruediv__(self, other):
		if isinstance(other, Number):
			return Vec3(other.value) / self
		return NotImplemented

	def __repr__(self):
		return f"{self.__class__.__name__}({self.x}, {self.y}, {self.z})"


class Vec4(Value):
	type = Vec4Type

	def __init__(self, *xyzw):
		assert 0 <= len(xyzw) <= 4
		assert all(isinstance(x, (int, float)) for x in xyzw)
		if len(xyzw) == 0:
			self.x, self.y, self.z, self.w = 0, 0, 0, 0
		elif len(xyzw) == 1:
			x = xyzw[0]
			self.x, self.y, self.z, self.w = x, x, x, x
		else:
			self.x, self.y, self.z, self.w = xyzw + (0,) * (4 - len(xyzw))

	@property
	def xyzw(self):
		return self.x, self.y, self.z, self.w

	def __add__(self, other):
		if isinstance(other, Vec4):
			return Vec4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)
		if isinstance(other, Vec3):
			return self + Vec4(*other.xyz)
		if isinstance(other, Number):
			return self + Vec4(other.value)
		return NotImplemented

	__radd__ = __add__

	def __sub__(self, other):
		if isinstance(other, Vec4):
			return Vec4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)
		if isinstance(other, Vec3):
			return self - Vec4(*other.xyz)
		if isinstance(other, Number):
			return self - Vec4(other.value)
		return NotImplemented

	def __rsub__(self, other):
		if isinstance(other, Number):
			return Vec4(other.value) - self
		if isinstance(other, Vec3):
			return Vec4(*other.xyz) - self
		return NotImplemented

	def __mul__(self, other):
		if isinstance(other, Vec4):
			return Vec4(self.x * other.x, self.y * other.y, self.z * other.z, self.w * other.w)
		if isinstance(other, Vec3):
			return self * Vec4(*other.xyz)
		if isinstance(other, Number):
			return self * Vec4(other.value)
		return NotImplemented

	__rmul__ = __mul__

	def __truediv__(self, other):
		if isinstance(other, Vec4):
			return Vec4(self.x / other.x, self.y / other.y, self.z / other.z, self.w / other.w)
		if isinstance(other, Vec3):
			return self / Vec4(*other.xyz)
		if isinstance(other, Number):
			return self / Vec4(other.value)
		return NotImplemented

	def __rtruediv__(self, other):
		if isinstance(other, Number):
			return Vec4(other.value) / self
		if isinstance(other, Vec3):
			return Vec4(*other.xyz) / self
		return NotImplemented

	def __repr__(self):
		return f"{self.__class__.__name__}({self.x}, {self.y}, {self.z}, {self.w})"


class Expression(Value):
	def eval(self):
		raise NotImplementedError


class BinOp(Expression):
	def __init__(self, op, lhs, rhs):
		assert op in "+-*/"
		self.op, self.lhs, self.rhs = op, lhs, rhs
		self.type # Triggers type checking

	def eval(self):
		if self.op == "+":
			return self.lhs.eval() + self.rhs.eval()
		if self.op == "-":
			return self.lhs.eval() - self.rhs.eval()
		if self.op == "*":
			return self.lhs.eval() * self.rhs.eval()
		if self.op == "/":
			return self.lhs.eval() / self.rhs.eval()

	@property
	def type(self):
		if self.op == "+":
			return self.lhs.type + self.rhs.type
		if self.op == "-":
			return self.lhs.type - self.rhs.type
		if self.op == "*":
			return self.lhs.type * self.rhs.type
		if self.op == "/":
			return self.lhs.type / self.rhs.type

	def __repr__(self):
		return f"{self.__class__.__name__}({self.op!r}, {self.lhs!r}, {self.rhs!r})"


class UnaryOp(Expression):
	def __init__(self, op, operand):
		assert op == "-"
		self.op, self.operand = op, operand
		self.type # Triggers type checking

	def eval(self):
		return -self.operand.eval()

	@property
	def type(self):
		return -self.operand.type

	def __repr__(self):
		return f"{self.__class__.__name__}({self.op!r}, {self.operand!r})"
