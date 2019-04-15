#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager, suppress

from .parser import parse, _units, Node, Create
from .datatypes import Value, Number, String, Time, TimeUnit, BinOp, UnaryOp, Call
from .element import Element, Percentage
from .templates import Template
from .functions import functions


class SceneBuilderError(Exception):
	pass


class SceneBuilder:
	def __init__(self):
		self.templates = None
		self._elements = None

	@property
	def _element(self):
		return self._elements[-1]

	@contextmanager
	def _push_element(self, element):
		self._elements.append(element)
		yield
		assert self._elements.pop() is element

	@staticmethod
	def _create_error(message, *, token=None):
		if token is not None:
			begin, end = token.span
			return SceneBuilderError("%s at %d:%d to %d:%d" % (message, *begin, *end))
		else:
			return SceneBuilderError(message)

	def _fail(self, message, *, token=None):
		raise self._create_error(message, token=token)

	def build(self, string):
		if isinstance(string, str):
			return self.build(parse(string))
		else:
			assert isinstance(string, Create)
			assert string.element == "Scene"

			self.templates = dict((template.__name__, template) for template in Template.list_templates())
			self._elements = []

			scene = self._build(string)

			assert isinstance(scene, Element)
			assert scene.type_name == "Scene"

			return scene

	def _build(self, node):
		assert isinstance(node, Node)
		method = "_build_%s" % node.__class__.__name__
		visitor = getattr(self, method)
		return visitor(node)

	def _build_children(self, node):
		for child in node.children:
			yield self._build(child)

	def _build_Create(self, create):
		template_name = create.element

		try:
			template = self.templates[create.element]
		except KeyError:
			raise self._create_error(f"Creating undefined {template_name!r} template", token=create.token) from None

		element = Element()

		if create.name:
			raise NotImplementedError

		parent = None
		with suppress(IndexError):
			parent = self._element

		if parent is not None:
			parent.add(element)

		template.apply(element)

		with self._push_element(element):
			for child in self._build_children(create):
				pass

		return element

	def _build_Template(self, template):
		raise NotImplementedError

	def _build_Assign(self, assign):
		name, value = self._build_children(assign)

		assert isinstance(name, str)
		assert isinstance(value, Value)

		try:
			self._element.set(name, value)
		except KeyError:
			raise self._create_error(f"Assigning value to undefined property {name!r} in {self._element.type_name}", token=assign.token) from None
		except TypeError as ex:
			raise self._create_error(f"{ex} in {self._element.type_name}", token=assign.token) from None

		return None

	def _build_Name(self, name):
		assert len(name.children) == 0
		return name.name

	def _build_UnaryOp(self, unary_op):
		assert len(unary_op.children) == 1
		operand, = self._build_children(unary_op)
		return UnaryOp(unary_op.op, operand)

	def _build_BinOp(self, bin_op):
		assert len(bin_op.children) == 2
		lhs, rhs = self._build_children(bin_op)
		return BinOp(bin_op.op, lhs, rhs)

	def _build_Number(self, number):
		assert len(number.children) == 0

		value, unit = number.value, number.unit

		if unit is None:
			return Number(value)
		elif unit == "%":
			return Percentage(value)
		elif unit in (unit.value for unit in TimeUnit):
			return Time(value, TimeUnit(unit))
		else:
			self._fail(f"Unexpected unit {unit!r}, expected any of {_units}", token=number.token)

		return number

	def _build_String(self, string):
		assert len(string.children) == 0
		return String(string.string)

	def _build_Call(self, call):
		args = tuple(self._build_children(call))
		return Call(functions[call.name], args)
