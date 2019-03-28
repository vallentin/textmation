#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ShorthandProperty:
	def __init__(self, *properties):
		assert len(properties) > 0
		self.properties = properties

	def __get__(self, instance, owner):
		if len(self.properties) == 1:
			return getattr(instance, self.properties[0])
		else:
			return tuple(getattr(instance, property) for property in self.properties)

	def __set__(self, instance, value):
		if len(self.properties) > 1 and isinstance(value, tuple):
			assert len(self.properties) == len(value)
			for i, property in enumerate(self.properties):
				setattr(instance, property, value[i])
		else:
			for property in self.properties:
				setattr(instance, property, value)


class NonNegative:
	def __get__(self, instance, owner):
		return instance.__dict__[self.name]

	def __set__(self, instance, value):
		if value < 0:
			raise ValueError("Value cannot be negative")
		instance.__dict__[self.name] = value

	def __set_name__(self, owner, name):
		self.name = name


class TypedProperty:
	def __init__(self, type):
		self.type = type

	def __get__(self, instance, owner):
		return instance.__dict__[self.name]

	def __set__(self, instance, value):
		if not isinstance(value, self.type):
			if isinstance(value, tuple):
				value = self.type(*value)
			else:
				value = self.type(value)
		instance.__dict__[self.name] = value

	def __set_name__(self, owner, name):
		self.name = name


class IntProperty(TypedProperty):
	def __init__(self):
		super().__init__(int)


class FloatProperty(TypedProperty):
	def __init__(self):
		super().__init__(float)
