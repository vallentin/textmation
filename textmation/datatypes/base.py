#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
