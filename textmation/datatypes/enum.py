#!/usr/bin/env python
# -*- coding: utf-8 -*-

import enum

from .base import *


class EnumType(Type):
	pass


class FlagType(Type):
	def __and__(self, other):
		if self is other:
			return self
		return NotImplemented

	__or__ = __and__


class Enum(Value):
	def __init__(self, value):
		assert isinstance(value, enum.Enum)
		assert isinstance(value.type, EnumType)
		self.value = value

	@property
	def type(self):
		return self.value.type

	def unbox(self):
		return self.value

	def is_constant(self):
		return True

	def __repr__(self):
		# return f"{self.__class__.__name__}({self.value.__class__.__name__}.{self.value._name_})"
		return f"{self.__class__.__name__}({self.value!s})"

	def __str__(self):
		# return f"{self.value.__class__.__name__}.{self.value._name_}"
		return f"{self.value!s}"


class Flag(Value):
	def __init__(self, value):
		assert isinstance(value, enum.Enum)
		assert isinstance(value.type, FlagType)
		self.value = value

	@property
	def type(self):
		return self.value.type

	@property
	def names(self):
		return self.type.names

	def unbox(self):
		return self.value

	def is_constant(self):
		return True

	def __and__(self, other):
		if isinstance(other, Flag):
			if self.type is other.type:
				return Flag(self.value & other.value)
		return NotImplemented

	def __or__(self, other):
		if isinstance(other, Flag):
			if self.type is other.type:
				return Flag(self.value | other.value)
		return NotImplemented

	def __repr__(self):
		return f"{self.__class__.__name__}({self.value!s})"

	def __str__(self):
		return f"{self.value!s}"


def register_enum(cls):
	_names = tuple(cls.__members__.keys())

	class _SpecializedEnumType(EnumType):
		name = cls.__name__
		names = _names
		enum = cls

	SpecializedEnum = _SpecializedEnumType()

	cls.type = SpecializedEnum

	cls.box = lambda self: Enum(self)

	return cls


def register_flag(cls):
	_names = tuple(cls.__members__.keys())

	class _SpecializedFlagType(FlagType):
		name = cls.__name__
		names = _names
		enum = cls

	SpecializedFlag = _SpecializedFlagType()

	cls.type = SpecializedFlag

	cls.box = lambda self: Flag(self)

	return cls
