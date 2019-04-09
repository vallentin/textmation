#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager
from inspect import isclass

from . import elements
from . import parser
from .elements import Element
from .parser import parse


internal_templates = {}

for name, cls in elements.__dict__.items():
	if not isclass(cls):
		continue
	if issubclass(cls, Element) and cls is not Element:
		internal_templates[name] = cls

internal_templates["Rect"] = internal_templates["Rectangle"]


class InterpreterError(Exception):
	pass


class Interpreter:
	def __init__(self):
		self._elements = None

	@property
	def _element(self):
		return self._elements[-1]

	@contextmanager
	def _push_element(self, element):
		self._elements.append(element)
		yield
		assert self._elements.pop() is element

	def interpret(self, string):
		if isinstance(string, str):
			return self.interpret(parse(string))
		else:
			assert isinstance(string, parser.Create)
			assert string.element == "Scene"

			self._elements = []

			scene = self._interpret(string)
			assert isinstance(scene, elements.Scene)

			return scene

	def _interpret(self, node):
		assert isinstance(node, parser.Node)
		method = "_interpret_%s" % node.__class__.__name__
		visitor = getattr(self, method)
		return visitor(node)

	def _interpret_children(self, node):
		for child in node.children:
			yield self._interpret(child)

	def _interpret_Create(self, create):
		template_name = create.element
		try:
			template = internal_templates[create.element]
		except KeyError:
			raise InterpreterError(f"Undefined {template_name!r} template") from None

		element = template()

		if create.name:
			raise NotImplementedError

		with self._push_element(element):
			for child in self._interpret_children(create):
				if child is None:
					continue
				assert isinstance(child, Element)
				element.add(child)

		return element

	def _interpret_Template(self, template):
		raise NotImplementedError

	def _interpret_BinOp(self, bin_op):
		raise NotImplementedError

	def _interpret_UnaryOp(self, unary_op):
		raise NotImplementedError

	def _interpret_Assign(self, assign):
		name, value = self._interpret_children(assign)
		self._element.set(name, value)
		return None

	def _interpret_Name(self, name):
		assert len(name.children) == 0
		return name.name

	def _interpret_Number(self, number):
		assert len(number.children) == 0
		return number

	def _interpret_String(self, string):
		assert len(string.children) == 0
		return string.string
