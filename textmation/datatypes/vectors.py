#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import *
from .scalars import *


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
