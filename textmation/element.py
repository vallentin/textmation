#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .binding import UnaryExpression, BinaryExpression
from .datatypes import *


class ElementProperty:
	def __init__(self, name, value, types, *, relative=None):
		assert isinstance(name, str)
		assert isinstance(types, tuple)
		assert len(types) > 0
		assert all(issubclass(type, Type) for type in types)
		assert relative is None or isinstance(relative, ElementProperty)

		self.name = name
		self.value = None
		self.types = types
		self.relative = relative

		self.set(value)

	def get(self):
		return self.value

	def set(self, value):
		# TODO: Check what the expression evaluates into
		if not isinstance(value, (UnaryExpression, BinaryExpression)):
			assert any(isinstance(value, type) for type in self.types)
		self.value = value

	def eval(self):
		return self.value.eval(self)

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.name!r}, {self.value!r}>"


class Element(Type):
	def __init__(self):
		super().__init__(self)

		self._properties = {}
		self._children = []
		self._parent = None

	def define(self, name, value, types=None, *, relative=None):
		if isinstance(value, (int, float)):
			value = Number(value)
		elif isinstance(value, str):
			value = String(value)

		assert isinstance(name, str)
		assert isinstance(value, Type)
		assert name not in self._properties

		if types is None:
			types = type(value),
		elif not isinstance(types, tuple):
			types = types,

		if isinstance(relative, str):
			relative = self.get("parent").eval().get(relative)

		property = ElementProperty(name, value, types, relative=relative)
		self._properties[name] = property

	def get(self, name):
		return self._properties[name]

	def set(self, name, value):
		assert name in self._properties

		if isinstance(value, (int, float)):
			value = Number(value)
		elif isinstance(value, str):
			value = String(value)

		self._properties[name].set(value)

	def has(self, name):
		return name in self._properties

	def add(self, element):
		assert isinstance(element, Element)
		assert element._parent is None

		element._parent = self
		self._children.append(element)

	def __repr__(self):
		name = self.get('name').eval() if self.has("name") else self.__class__.__name__
		return f"<{name}: 0x{id(self):X}>"
