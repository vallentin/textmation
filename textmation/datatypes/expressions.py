#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import *


class Expression(Value):
	def eval(self):
		raise NotImplementedError

	def fold(self):
		raise NotImplementedError

	def is_constant(self):
		raise NotImplementedError

	def apply(self, relative):
		raise NotImplementedError


class BinOp(Expression):
	def __init__(self, op, lhs, rhs):
		assert op in ("+", "-", "*", "/", "//", "%", "&", "|")
		assert isinstance(lhs, Value)
		assert isinstance(rhs, Value)
		self.op, self.lhs, self.rhs = op, lhs, rhs
		self.type # Triggers type checking

	@property
	def type(self):
		if self.op == "+":
			return self.lhs.type + self.rhs.type
		if self.op == "-":
			return self.lhs.type - self.rhs.type
		if self.op == "*":
			return self.lhs.type * self.rhs.type
		if self.op == "/":
			return self.lhs.type / self.rhs.type
		if self.op == "//":
			return self.lhs.type // self.rhs.type
		if self.op == "%":
			return self.lhs.type % self.rhs.type
		if self.op == "&":
			return self.lhs.type & self.rhs.type
		if self.op == "|":
			return self.lhs.type | self.rhs.type
		raise NotImplementedError

	def eval(self):
		if self.op == "+":
			return self.lhs.eval() + self.rhs.eval()
		if self.op == "-":
			return self.lhs.eval() - self.rhs.eval()
		if self.op == "*":
			return self.lhs.eval() * self.rhs.eval()
		if self.op == "/":
			return self.lhs.eval() / self.rhs.eval()
		if self.op == "//":
			return self.lhs.eval() // self.rhs.eval()
		if self.op == "%":
			return self.lhs.eval() % self.rhs.eval()
		if self.op == "&":
			return self.lhs.eval() & self.rhs.eval()
		if self.op == "|":
			return self.lhs.eval() | self.rhs.eval()
		raise NotImplementedError

	def fold(self):
		if self.is_constant():
			return self.eval()
		return BinOp(self.op, self.lhs.fold(), self.rhs.fold())

	def is_constant(self):
		return self.lhs.is_constant() and self.rhs.is_constant()

	def apply(self, relative):
		self.lhs.apply(relative)
		self.rhs.apply(relative)

	def iter_values(self):
		yield self.lhs
		yield self.rhs

	def __repr__(self):
		return f"{self.__class__.__name__}({self.op!r}, {self.lhs!r}, {self.rhs!r})"


class UnaryOp(Expression):
	def __init__(self, op, operand):
		assert op == "-"
		assert isinstance(operand, Value)
		self.op, self.operand = op, operand
		self.type # Triggers type checking

	@property
	def type(self):
		return -self.operand.type

	def eval(self):
		return -self.operand.eval()

	def fold(self):
		if self.is_constant():
			return self.eval()
		return UnaryOp(self.op, self.operand.fold())

	def is_constant(self):
		return self.operand.is_constant()

	def apply(self, relative):
		self.operand.apply(relative)

	def iter_values(self):
		yield self.operand

	def __repr__(self):
		return f"{self.__class__.__name__}({self.op!r}, {self.operand!r})"


class Call(Expression):
	def __init__(self, func, args=()):
		self.func = func
		self.args = tuple(args)
		self.func.type_check(self.args)

	@property
	def type(self):
		return self.func.return_type

	def eval(self):
		return self.func(*(arg.eval() for arg in self.args))

	def fold(self):
		if self.is_constant():
			return self.eval()
		args = [arg.fold() for arg in self.args]
		return Call(self.func, args)

	def is_constant(self):
		for arg in self.args:
			if not arg.is_constant():
				return False
		return True

	def apply(self, relative):
		for arg in self.args:
			arg.apply(relative)

	def iter_values(self):
		for arg in self.args:
			yield arg

	def __repr__(self):
		return f"{self.__class__.__name__}({self.func.name!r}, {self.args!r})"
