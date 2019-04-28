#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import *


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
