#!/usr/bin/env python
# -*- coding: utf-8 -*-

import operator


class CircularBindingError(Exception):
	pass


class Binding:
	def get(self):
		raise NotImplementedError

	def traverse(self):
		yield self

	def __pos__(self):
		return UnaryExpression(operator.pos, self)

	def __neg__(self):
		return UnaryExpression(operator.neg, self)

	def __add__(self, other):
		return BinaryExpression(operator.add, self, other)

	def __radd__(self, other):
		return BinaryExpression(operator.add, other, self)

	def __sub__(self, other):
		return BinaryExpression(operator.sub, self, other)

	def __rsub__(self, other):
		return BinaryExpression(operator.sub, other, self)

	def __mul__(self, other):
		return BinaryExpression(operator.mul, self, other)

	def __rmul__(self, other):
		return BinaryExpression(operator.mul, other, self)

	def __truediv__(self, other):
		return BinaryExpression(operator.truediv, self, other)

	def __rtruediv__(self, other):
		return BinaryExpression(operator.truediv, other, self)

	def __floordiv__(self, other):
		return BinaryExpression(operator.floordiv, self, other)

	def __rfloordiv__(self, other):
		return BinaryExpression(operator.floordiv, other, self)

	def __mod__(self, other):
		return BinaryExpression(operator.mod, self, other)

	def __rmod__(self, other):
		return BinaryExpression(operator.mod, other, self)

	def __repr__(self):
		# return f"<{self.__class__.__name__}: {self.get()!r}>"
		return repr(self.get())

	def __str__(self):
		return str(self.get())


class UnaryExpression(Binding):
	def __init__(self, op, operand):
		self.op, self.operand = op, operand

	def get(self):
		operand = self.operand
		if isinstance(operand, Binding):
			operand = operand.get()
		return self.op(operand)

	def traverse(self):
		yield self
		if isinstance(self.operand, Binding):
			yield from self.operand.traverse()


class BinaryExpression(Binding):
	def __init__(self, op, lhs, rhs):
		self.op, self.lhs, self.rhs = op, lhs, rhs

	def get(self):
		lhs = self.lhs
		if isinstance(lhs, Binding):
			lhs = lhs.get()
		rhs = self.rhs
		if isinstance(rhs, Binding):
			rhs = rhs.get()
		return self.op(lhs, rhs)

	def traverse(self):
		yield self
		if isinstance(self.lhs, Binding):
			yield from self.lhs.traverse()
		if isinstance(self.rhs, Binding):
			yield from self.rhs.traverse()


class Property(Binding):
	def __init__(self, value):
		self.value = value

	def get(self):
		return self.value

	def set(self, value):
		if isinstance(value, Binding):
			path = {self}
			for node in value.traverse():
				if node in path:
					raise CircularBindingError
				path.add(node)
		self.value = value
		return self.value

	def traverse(self):
		yield self
		if isinstance(self.value, Binding):
			yield from self.value.traverse()


if __name__ == "__main__":
	width = Property(10)
	height = Property(5)

	area = width * height

	print(width)
	print(height)
	print(area)
	print()

	height.set(20)

	print(width)
	print(height)
	print(area)
	print()

	# Triggers CircularBindingError
	# width.set(height * 2)
	# height.set(width * 2)
