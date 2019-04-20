#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager
from operator import attrgetter

from ..datatypes import Type, Value, Number, String
from ..utilities import iter_all_subclasses


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


class ElementError(Exception):
	pass


class ElementPropertyDefinedError(Exception):
	pass


class CircularReferenceError(Exception):
	def __init__(self, message, paths):
		super().__init__(message)
		self.paths = paths


def _iter_cycles(current, target, path):
	for value in current.iter_values():
		new_path = path + [value]
		if value == target:
			yield new_path
		elif value in path:
			continue
		else:
			yield from _iter_cycles(value, target, new_path)


def find_cycles(value):
	paths = []
	for path in _iter_cycles(value, value, [value]):
		path = tuple(node for node in path if isinstance(node, ElementProperty))
		if path not in paths:
			paths.append(path)
	return paths


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
		self.check_value(value)

		self.value = value
		self.value.apply(self.relative)

		paths = find_cycles(self)
		if paths:
			raise CircularReferenceError(f"Circular dependency encountered", paths)

	def check_value(self, value):
		if isinstance(value, (int, float)):
			value = Number(value)
		elif isinstance(value, str):
			value = String(value)

		assert isinstance(value, Value)

		if not any(value.type is type for type in self.types):
			type_names = ", ".join(map(attrgetter("name"), self.types))
			raise TypeError(f"Expected type of {type_names}, received {value.type.name}")

	def eval(self):
		return self.value.eval()

	def iter_values(self):
		yield self.value

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.name!r}, {self.value!r}>"


class _Element(Type):
	pass


ElementType = _Element()


class Element(Value):
	@staticmethod
	def list_element_types():
		return list(iter_all_subclasses(Element))

	type = ElementType

	def __init__(self):
		self.properties = {}
		self.computed_properties = {}
		self.children = []
		self.parent = None

	def on_init(self):
		pass

	def on_ready(self):
		if self.parent is not None:
			self.define("parent", self.parent)

	def on_created(self):
		pass

	def define(self, name, value, types=None, *, relative=None):
		if name in self.properties:
			raise ElementPropertyDefinedError(f"Property {name!r} is already defined")

		if isinstance(value, (int, float)):
			value = Number(value)
		elif isinstance(value, str):
			value = String(value)

		assert isinstance(name, str)

		if isinstance(relative, str):
			assert self.parent is not None
			relative = self.parent.get(relative)

		self.properties[name] = ElementProperty(name, value, types, relative=relative)
		self.computed_properties[name] = ElementProperty(name, value, types, relative=relative)

	def get(self, name):
		return self.properties[name]

	def set(self, name, value):
		assert isinstance(name, str)
		self.get(name).set(value)

	def check_value(self, name, value):
		assert isinstance(name, str)
		self.get(name).check_value(value)

	# def has(self, name):
	# 	return name in self.properties

	def eval(self, name=None):
		if name is None:
			return self
		return self.get(name).eval()

	def __getattr__(self, name):
		if name.startswith("p_"):
			return self.eval(name[2:]).unbox()
		return self.__getattribute__(name)

	def add(self, element):
		assert isinstance(element, Element)
		assert element.parent is None

		element.parent = self
		self.children.append(element)

	def traverse(self):
		yield self
		for child in self.children:
			yield from child.traverse()

	def compute(self, time):
		for name, property in self.properties.items():
			self.computed_properties[name].set(property.eval())
		self.compute_children(time)

	def compute_children(self, time):
		for child in self.children:
			child.compute(time)

	def __repr__(self):
		return f"<{self.__class__.__name__}: 0x{id(self):X}>"
