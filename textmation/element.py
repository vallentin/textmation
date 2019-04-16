#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager
from operator import attrgetter

from .datatypes import Type, Value, Number, String


class Percentage(Number):
	def __init__(self, value):
		super().__init__(value)
		self.relative = None

	def eval(self):
		assert isinstance(self.relative, ElementProperty)
		# return BinOp("*", self.relative.eval(), BinOp("/", Number(self.value), Number(100))).eval()
		return self.relative.eval() * (self / Number(100))

	def apply(self, relative):
		assert isinstance(relative, ElementProperty)
		self.relative = relative


class ElementProperty(Value):
	def __init__(self, name, value, types=None, *, relative=None):
		assert isinstance(name, str)
		assert isinstance(value, Value)

		if types is None:
			types = value.type,
		elif not isinstance(types, tuple):
			types = types,

		types = tuple(type if isinstance(type, Type) else type.type for type in types)

		assert isinstance(types, tuple)
		assert len(types) > 0
		assert all(isinstance(type, Type) for type in types)
		assert relative is None or isinstance(relative, ElementProperty)

		self.name = name
		self.value = None
		self.types = types
		self.relative = relative

		self.set(value)

	@property
	def type(self):
		return self.value.type

	def get(self):
		return self.value

	def set(self, value):
		if isinstance(value, (int, float)):
			value = Number(value)
		elif isinstance(value, str):
			value = String(value)

		assert isinstance(value, Value)

		if not any(value.type is type for type in self.types):
			type_names = ", ".join(map(attrgetter("name"), self.types))
			raise TypeError(f"Expected type of {type_names}, received {value.type.name}")

		self.value = value
		self.value.apply(self.relative)

	def eval(self):
		return self.value.eval()

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.name!r}, {self.value!r}>"


class Element:
	def __init__(self):
		self._properties = {}
		self._children = []
		self._parent = None

	def define(self, name, value, types=None, *, relative=None):
		if isinstance(value, (int, float)):
			value = Number(value)
		elif isinstance(value, str):
			value = String(value)

		assert isinstance(name, str)
		assert name not in self._properties

		if isinstance(relative, str):
			assert self._parent is not None
			relative = self._parent.get(relative)

		property = ElementProperty(name, value, types, relative=relative)
		self._properties[name] = property

	def get(self, name):
		return self._properties[name]

	def set(self, name, value):
		assert isinstance(name, str)
		self.get(name).set(value)

	def has(self, name):
		return name in self._properties

	def eval(self, name):
		return self.get(name).eval()

	def __getattr__(self, name):
		if name.startswith("p_"):
			return self.eval(name[2:]).unbox()
		return self.__getattribute__(name)

	def add(self, element):
		assert isinstance(element, Element)
		assert element._parent is None

		element._parent = self
		self._children.append(element)

	@property
	def type_name(self):
		if self.has("type"):
			name = self.get("type").eval()
			assert isinstance(name, String)
			return name.string
		return self.__class__.__name__

	def __repr__(self):
		return f"<{self.type_name}: 0x{id(self):X}>"
