#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import total_ordering
from enum import Enum
import math

from .base import *


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
		return f"{self.duration}{self.unit.value}"

	def __repr__(self):
		return f"{self.__class__.__name__}({self.duration!r}, {self.unit})"
