#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Type:
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
