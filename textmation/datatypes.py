#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
from functools import total_ordering
import math


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

	def unbox(self):
		return self

	def eval(self):
		return self

	def fold(self):
		return self

	def is_constant(self):
		raise NotImplementedError

	def apply(self, relative):
		pass

	def iter_values(self):
		return
		yield


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
	__mod__ = __add__
	__rmod__ = __add__

	def __neg__(self):
		return NumberType


NumberType = _Number()


class Number(Value):
	type = NumberType

	def __init__(self, value):
		assert isinstance(value, (int, float))
		self.value = value

	def unbox(self):
		return self.value

	def is_constant(self):
		return True

	def __add__(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value)
		if isinstance(other, (int, float)):
			return Number(self.value + other)
		return NotImplemented

	__radd__ = __add__

	def __sub__(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value)
		if isinstance(other, (int, float)):
			return Number(self.value - other)
		return NotImplemented

	def __rsub__(self, other):
		if isinstance(other, Number):
			return Number(other.value - self.value)
		if isinstance(other, (int, float)):
			return Number(other - self.value)
		return NotImplemented

	def __mul__(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value)
		if isinstance(other, (int, float)):
			return Number(self.value * other)
		return NotImplemented

	__rmul__ = __mul__

	def __truediv__(self, other):
		if isinstance(other, Number):
			return Number(self.value / other.value)
		if isinstance(other, (int, float)):
			return Number(self.value / other)
		return NotImplemented

	def __rtruediv__(self, other):
		if isinstance(other, Number):
			return Number(other.value / self.value)
		if isinstance(other, (int, float)):
			return Number(other / self.value)
		return NotImplemented

	def __floordiv__(self, other):
		if isinstance(other, Number):
			return Number(self.value // other.value)
		if isinstance(other, (int, float)):
			return Number(self.value // other)
		return NotImplemented

	def __rfloordiv__(self, other):
		if isinstance(other, Number):
			return Number(other.value // self.value)
		if isinstance(other, (int, float)):
			return Number(other // self.value)
		return NotImplemented

	def __mod__(self, other):
		if isinstance(other, Number):
			return Number(self.value % other.value)
		if isinstance(other, (int, float)):
			return Number(self.value % other)
		return NotImplemented

	def __rmod__(self, other):
		if isinstance(other, Number):
			return Number(other.value % self.value)
		if isinstance(other, (int, float)):
			return Number(other % self.value)
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

	def unbox(self):
		return self.string

	def is_constant(self):
		return True

	def __add__(self, other):
		return String(self.string + str(other))

	def __radd__(self, other):
		return String(str(other) + self.string)

	def __str__(self):
		return self.string

	def __repr__(self):
		return f"{self.__class__.__name__}({self.string!r})"


class _Angle(Type):
	def __add__(self, other):
		if other is AngleType:
			return AngleType
		return NotImplemented

	def __sub__(self, other):
		if other is AngleType:
			return AngleType
		return NotImplemented

	def __mul__(self, other):
		if other is NumberType:
			return AngleType
		return NotImplemented

	__rmul__ = __mul__

	def __truediv__(self, other):
		if other is NumberType:
			return AngleType
		return NotImplemented

	def __neg__(self):
		return AngleType


AngleType = _Angle()


class AngleUnit(Enum):
	Degrees = "deg"
	Radians = "rad"
	Turns = "turn"


class Angle(Value):
	type = AngleType

	def __init__(self, angle, unit):
		assert isinstance(angle, (int, float))
		assert isinstance(unit, AngleUnit)
		self.angle = angle
		self.unit = unit

	@property
	def degrees(self):
		if self.unit == AngleUnit.Degrees:
			return self.angle
		if self.unit == AngleUnit.Radians:
			return math.degrees(self.angle)
		if self.unit == AngleUnit.Turns:
			return self.angle * 360
		raise NotImplementedError

	@property
	def radians(self):
		if self.unit == AngleUnit.Radians:
			return self.angle
		if self.unit == AngleUnit.Degrees:
			return math.radians(self.angle)
		if self.unit == AngleUnit.Turns:
			return self.angle * math.tau
		raise NotImplementedError

	@property
	def turns(self):
		if self.unit == AngleUnit.Turns:
			return self.angle
		if self.unit == AngleUnit.Degrees:
			return self.angle / 360
		if self.unit == AngleUnit.Radians:
			return self.angle / math.tau
		raise NotImplementedError

	def is_constant(self):
		return True

	def __add__(self, other):
		if isinstance(other, Angle):
			return Angle(self.degrees + other.degrees, AngleUnit.Degrees)
		return NotImplemented

	def __sub__(self, other):
		if isinstance(other, Angle):
			return Angle(self.degrees - other.degrees, AngleUnit.Degrees)
		return NotImplemented

	def __mul__(self, other):
		if isinstance(other, Number):
			return Angle(self.angle * other.value, self.unit)
		if isinstance(other, (int, float)):
			return Angle(self.angle * other, self.unit)
		return NotImplemented

	__rmul__ = __mul__

	def __truediv__(self, other):
		if isinstance(other, Number):
			return Angle(self.angle / other.value, self.unit)
		if isinstance(other, (int, float)):
			return Angle(self.angle / other, self.unit)
		return NotImplemented

	def __neg__(self):
		return Angle(-self.angle, self.unit)

	def __str__(self):
		return f"{self.angle}{self.unit.value}"

	def __repr__(self):
		return f"{self.__class__.__name__}({self.angle!r}, {self.unit})"


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


@total_ordering
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

	def is_constant(self):
		return True

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

	def __lt__(self, other):
		if isinstance(other, Time):
			return self.milliseconds < other.milliseconds
		return NotImplemented

	def __str__(self):
		# TODO: pprint float
		# TODO: https://stackoverflow.com/questions/2440692/formatting-floats-in-python-without-superfluous-zeros
		return f"{self.duration}{self.unit.value}"

	def __repr__(self):
		return f"{self.__class__.__name__}({self.duration!r}, {self.unit})"


class _Vec2(Type):
	def __add__(self, other):
		if other in (Vec2Type, NumberType):
			return Vec2Type
		return NotImplemented

	__radd__ = __add__
	__sub__ = __add__
	__rsub__ = __add__
	__mul__ = __add__
	__rmul__ = __add__
	__truediv__ = __add__
	__rtruediv__ = __add__

	def __neg__(self):
		return Vec2Type


class _Vec3(Type):
	def __add__(self, other):
		if other in (Vec3Type, Vec2Type, NumberType):
			return Vec3Type
		return NotImplemented

	__radd__ = __add__
	__sub__ = __add__
	__rsub__ = __add__
	__mul__ = __add__
	__rmul__ = __add__
	__truediv__ = __add__
	__rtruediv__ = __add__

	def __neg__(self):
		return Vec3Type


class _Vec4(Type):
	def __add__(self, other):
		if other in (Vec4Type, Vec3Type, Vec2Type, NumberType):
			return Vec4Type
		return NotImplemented

	__radd__ = __add__
	__sub__ = __add__
	__rsub__ = __add__
	__mul__ = __add__
	__rmul__ = __add__
	__truediv__ = __add__
	__rtruediv__ = __add__

	def __neg__(self):
		return Vec4Type


Vec2Type = _Vec2()
Vec3Type = _Vec3()
Vec4Type = _Vec4()


class Vec2(Value):
	type = Vec2Type

	def __init__(self, *xy):
		assert 0 <= len(xy) <= 2
		assert all(isinstance(x, (int, float)) for x in xy)
		if len(xy) == 0:
			self.x, self.y = 0, 0
		elif len(xy) == 1:
			x = xy[0]
			self.x, self.y = x, x
		elif len(xy) == 2:
			self.x, self.y = xy

	@property
	def xy(self):
		return self.x, self.y

	@property
	def r(self):
		return self.x

	@property
	def g(self):
		return self.y

	@property
	def rg(self):
		return self.xy

	def is_constant(self):
		return True

	def __add__(self, other):
		if isinstance(other, Vec2):
			return Vec2(self.x + other.x, self.y + other.y)
		if isinstance(other, Number):
			return self + Vec2(other.value)
		if isinstance(other, (int, float)):
			return self + Vec2(other)
		return NotImplemented

	__radd__ = __add__

	def __sub__(self, other):
		if isinstance(other, Vec2):
			return Vec2(self.x - other.x, self.y - other.y)
		if isinstance(other, Number):
			return self - Vec2(other.value)
		if isinstance(other, (int, float)):
			return self - Vec2(other)
		return NotImplemented

	def __rsub__(self, other):
		if isinstance(other, Number):
			return Vec2(other.value) - self
		if isinstance(other, (int, float)):
			return Vec2(other) - self
		return NotImplemented

	def __mul__(self, other):
		if isinstance(other, Vec2):
			return Vec2(self.x * other.x, self.y * other.y)
		if isinstance(other, Number):
			return self * Vec2(other.value)
		if isinstance(other, (int, float)):
			return self * Vec2(other)
		return NotImplemented

	__rmul__ = __mul__

	def __truediv__(self, other):
		if isinstance(other, Vec2):
			return Vec2(self.x / other.x, self.y / other.y)
		if isinstance(other, Number):
			return self / Vec2(other.value)
		if isinstance(other, (int, float)):
			return self / Vec2(other)
		return NotImplemented

	def __rtruediv__(self, other):
		if isinstance(other, Number):
			return Vec2(other.value) / self
		if isinstance(other, (int, float)):
			return Vec2(other) / self
		return NotImplemented

	def __neg__(self):
		return Vec2(-self.x, -self.y)

	def __iter__(self):
		yield from self.xy

	def __repr__(self):
		return f"{self.__class__.__name__}({self.x}, {self.y})"


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

	@property
	def r(self):
		return self.x

	@property
	def g(self):
		return self.y

	@property
	def b(self):
		return self.z

	@property
	def rgb(self):
		return self.xyz

	def is_constant(self):
		return True

	def __add__(self, other):
		if isinstance(other, Vec3):
			return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
		if isinstance(other, Vec2):
			return self + Vec3(*other.xy)
		if isinstance(other, Number):
			return self + Vec3(other.value)
		if isinstance(other, (int, float)):
			return self + Vec3(other)
		return NotImplemented

	__radd__ = __add__

	def __sub__(self, other):
		if isinstance(other, Vec3):
			return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
		if isinstance(other, Vec2):
			return self - Vec3(*other.xy)
		if isinstance(other, Number):
			return self - Vec3(other.value)
		if isinstance(other, (int, float)):
			return self - Vec3(other)
		return NotImplemented

	def __rsub__(self, other):
		if isinstance(other, Vec2):
			return Vec3(*other.xy) - self
		if isinstance(other, Number):
			return Vec3(other.value) - self
		if isinstance(other, (int, float)):
			return Vec3(other) - self
		return NotImplemented

	def __mul__(self, other):
		if isinstance(other, Vec3):
			return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)
		if isinstance(other, Vec2):
			return self * Vec3(*other.xy)
		if isinstance(other, Number):
			return self * Vec3(other.value)
		if isinstance(other, (int, float)):
			return self * Vec3(other)
		return NotImplemented

	__rmul__ = __mul__

	def __truediv__(self, other):
		if isinstance(other, Vec3):
			return Vec3(self.x / other.x, self.y / other.y, self.z / other.z)
		if isinstance(other, Vec2):
			return self / Vec3(*other.xy)
		if isinstance(other, Number):
			return self / Vec3(other.value)
		if isinstance(other, (int, float)):
			return self / Vec3(other)
		return NotImplemented

	def __rtruediv__(self, other):
		if isinstance(other, Vec2):
			return Vec3(*other.xy) / self
		if isinstance(other, Number):
			return Vec3(other.value) / self
		if isinstance(other, (int, float)):
			return Vec3(other) / self
		return NotImplemented

	def __neg__(self):
		return Vec3(-self.x, -self.y, -self.z)

	def __iter__(self):
		yield from self.xyz

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
	def xyz(self):
		return self.x, self.y, self.z

	@property
	def xyzw(self):
		return self.x, self.y, self.z, self.w

	@property
	def r(self):
		return self.x

	@property
	def g(self):
		return self.y

	@property
	def b(self):
		return self.z

	@property
	def a(self):
		return self.w

	@property
	def rgb(self):
		return self.xyz

	@property
	def rgba(self):
		return self.xyzw

	def is_constant(self):
		return True

	def __add__(self, other):
		if isinstance(other, Vec4):
			return Vec4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)
		if isinstance(other, Vec3):
			return self + Vec4(*other.xyz)
		if isinstance(other, Vec2):
			return self + Vec4(*other.xy)
		if isinstance(other, Number):
			return self + Vec4(other.value)
		if isinstance(other, (int, float)):
			return self + Vec4(other)
		return NotImplemented

	__radd__ = __add__

	def __sub__(self, other):
		if isinstance(other, Vec4):
			return Vec4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)
		if isinstance(other, Vec3):
			return self - Vec4(*other.xyz)
		if isinstance(other, Vec2):
			return self - Vec4(*other.xy)
		if isinstance(other, Number):
			return self - Vec4(other.value)
		if isinstance(other, (int, float)):
			return self - Vec4(other)
		return NotImplemented

	def __rsub__(self, other):
		if isinstance(other, Vec3):
			return Vec4(*other.xyz) - self
		if isinstance(other, Vec2):
			return Vec4(*other.xy) - self
		if isinstance(other, Number):
			return Vec4(other.value) - self
		if isinstance(other, (int, float)):
			return Vec4(other) - self
		return NotImplemented

	def __mul__(self, other):
		if isinstance(other, Vec4):
			return Vec4(self.x * other.x, self.y * other.y, self.z * other.z, self.w * other.w)
		if isinstance(other, Vec3):
			return self * Vec4(*other.xyz)
		if isinstance(other, Vec2):
			return self * Vec4(*other.xy)
		if isinstance(other, Number):
			return self * Vec4(other.value)
		if isinstance(other, (int, float)):
			return self * Vec4(other)
		return NotImplemented

	__rmul__ = __mul__

	def __truediv__(self, other):
		if isinstance(other, Vec4):
			return Vec4(self.x / other.x, self.y / other.y, self.z / other.z, self.w / other.w)
		if isinstance(other, Vec3):
			return self / Vec4(*other.xyz)
		if isinstance(other, Vec2):
			return self / Vec4(*other.xy)
		if isinstance(other, Number):
			return self / Vec4(other.value)
		if isinstance(other, (int, float)):
			return self / Vec4(other)
		return NotImplemented

	def __rtruediv__(self, other):
		if isinstance(other, Vec3):
			return Vec4(*other.xyz) / self
		if isinstance(other, Vec2):
			return Vec4(*other.xy) / self
		if isinstance(other, Number):
			return Vec4(other.value) / self
		if isinstance(other, (int, float)):
			return Vec4(other) / self
		return NotImplemented

	def __neg__(self):
		return Vec4(-self.x, -self.y, -self.z, -self.w)

	def __iter__(self):
		yield from self.xyzw

	def __repr__(self):
		return f"{self.__class__.__name__}({self.x}, {self.y}, {self.z}, {self.w})"


class Color(Vec4):
	def __init__(self, r=0, g=None, b=None, a=255):
		if b is None:
			b = r if g is None else 0
		if g is None:
			g = r

		super().__init__(r, g, b, a)


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


class Expression(Value):
	def eval(self):
		raise NotImplementedError

	def fold(self):
		raise NotImplementedError

	def is_constant(self):
		raise NotImplementedError

	def apply(self, relative):
		raise NotImplementedError


class BinOp(Expression):
	def __init__(self, op, lhs, rhs):
		assert op in ("+", "-", "*", "/", "//", "%")
		assert isinstance(lhs, Value)
		assert isinstance(rhs, Value)
		self.op, self.lhs, self.rhs = op, lhs, rhs
		self.type # Triggers type checking

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
		if self.op == "//":
			return self.lhs.type // self.rhs.type
		if self.op == "%":
			return self.lhs.type % self.rhs.type

	def eval(self):
		if self.op == "+":
			return self.lhs.eval() + self.rhs.eval()
		if self.op == "-":
			return self.lhs.eval() - self.rhs.eval()
		if self.op == "*":
			return self.lhs.eval() * self.rhs.eval()
		if self.op == "/":
			return self.lhs.eval() / self.rhs.eval()
		if self.op == "//":
			return self.lhs.eval() // self.rhs.eval()
		if self.op == "%":
			return self.lhs.eval() % self.rhs.eval()

	def fold(self):
		if self.is_constant():
			return self.eval()
		return BinOp(self.op, self.lhs.fold(), self.rhs.fold())

	def is_constant(self):
		return self.lhs.is_constant() and self.rhs.is_constant()

	def apply(self, relative):
		self.lhs.apply(relative)
		self.rhs.apply(relative)

	def iter_values(self):
		yield self.lhs
		yield self.rhs

	def __repr__(self):
		return f"{self.__class__.__name__}({self.op!r}, {self.lhs!r}, {self.rhs!r})"


class UnaryOp(Expression):
	def __init__(self, op, operand):
		assert op == "-"
		assert isinstance(operand, Value)
		self.op, self.operand = op, operand
		self.type # Triggers type checking

	@property
	def type(self):
		return -self.operand.type

	def eval(self):
		return -self.operand.eval()

	def fold(self):
		if self.is_constant():
			return self.eval()
		return UnaryOp(self.op, self.operand.fold())

	def is_constant(self):
		return self.operand.is_constant()

	def apply(self, relative):
		self.operand.apply(relative)

	def iter_values(self):
		yield self.operand

	def __repr__(self):
		return f"{self.__class__.__name__}({self.op!r}, {self.operand!r})"


class Call(Expression):
	def __init__(self, func, args=()):
		self.func = func
		self.args = tuple(args)
		self.func.type_check(self.args)

	@property
	def type(self):
		return self.func.return_type

	def eval(self):
		return self.func(*(arg.eval() for arg in self.args))

	def fold(self):
		if self.is_constant():
			return self.eval()
		args = [arg.fold() for arg in self.args]
		return Call(self.func, args)

	def is_constant(self):
		for arg in self.args:
			if not arg.is_constant():
				return False
		return True

	def apply(self, relative):
		for arg in self.args:
			arg.apply(relative)

	def iter_values(self):
		for arg in self.args:
			yield arg

	def __repr__(self):
		return f"{self.__class__.__name__}({self.func.name!r}, {self.args!r})"
