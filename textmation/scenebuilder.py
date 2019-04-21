#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager, suppress
from operator import attrgetter

from .parser import parse, _units, Node, Create, Template, Name
from .datatypes import Value, Number, String, Angle, AngleUnit, Time, TimeUnit, BinOp, UnaryOp, Call
from .elements import Element, Scene, Percentage, ElementError, ElementPropertyDefinedError, CircularReferenceError
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

	def _get_template(self, name, *, token=None):
		try:
			return self.templates[name]
		except KeyError:
			raise self._create_error(f"Creating undefined {name!r} template", token=token) from None

	def _get_element_type(self, name, *, token=None):
		template = self._get_template(name, token=token)
		if isinstance(template, Template):
			return self._get_element_type(template.inherit or "Drawable")
		assert issubclass(template, Element)
		return template

	def _apply_template(self, element, template, *, token=None):
		if isinstance(template, str):
			try:
				template = self.templates[template]
			except KeyError:
				raise self._create_error(f"Creating undefined {template!r} template", token=token) from None

		if isinstance(template, Template):
			with self._push_element(element):
				self._apply_template(element, template.inherit or "Drawable", token=token)

				for child in self._build_children(template):
					pass
		else:
			element.on_ready()

	def _get_property(self, element, name, *, token=None):
		assert isinstance(element, Element)

		while element is not None:
			with suppress(KeyError):
				return element.get(name)
			element = element.parent

		self._fail(f"Undefined property {name!r}", token=token)

	@staticmethod
	def _create_error(message, *, after=None, token=None):
		if token is not None:
			begin, end = token.span
			if after:
				return SceneBuilderError("%s at %d:%d to %d:%d\n%s" % (message, *begin, *end, after))
			else:
				return SceneBuilderError("%s at %d:%d to %d:%d" % (message, *begin, *end))
		elif after:
			return SceneBuilderError(f"{message}\n{after}")
		else:
			return SceneBuilderError(message)

	def _fail(self, message, *, after=None, token=None):
		raise self._create_error(message, after=after, token=token)

	def build(self, string):
		if isinstance(string, str):
			return self.build(parse(string))
		else:
			assert isinstance(string, Create)
			assert string.element == "Scene"

			self.templates = dict((template.__name__, template) for template in Element.list_element_types())
			self._elements = []

			scene = self._build(string)

			assert isinstance(scene, Scene)

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
		if create.name:
			raise NotImplementedError

		element_type = self._get_element_type(create.element, token=create.token)

		element = element_type()
		element.on_init()

		parent = None
		with suppress(IndexError):
			parent = self._element
		if parent is not None:
			try:
				parent.add(element)
			except NotImplementedError:
				raise self._create_error(f"Cannot add {element.__class__.__name__} to {parent.__class__.__name__}", token=create.token) from None

		self._apply_template(element, create.element, token=create.token)

		with self._push_element(element):
			for child in self._build_children(create):
				pass

		try:
			element.on_created()
		except ElementError as ex:
			raise self._create_error(f"{ex} in {element.__class__.__name__}", token=create.token) from None

		return element

	def _build_Template(self, template):
		if template.name in self.templates:
			self._fail(f"Redeclaration of {template.name!r}", token=template.token)

		self.templates[template.name] = template

		return None

	def _build_Define(self, define):
		assert len(define.children) == 2

		name = define.name
		assert isinstance(name, Name)
		name = name.name

		value = self._build(define.value)

		assert isinstance(name, str)
		assert isinstance(value, Value)

		try:
			self._element.define(name, value)
		except ElementPropertyDefinedError as ex:
			raise self._create_error(f"{ex} in {self._element.__class__.__name__}", token=define.token) from None

		return None

	def _build_Assign(self, assign):
		assert len(assign.children) == 2

		name = assign.name
		assert isinstance(name, Name)
		name = name.name

		value = self._build(assign.value)

		assert isinstance(name, str)
		assert isinstance(value, Value)

		try:
			self._element.set(name, value)
		except KeyError:
			raise self._create_error(f"Assigning value to undefined property {name!r} in {self._element.__class__.__name__}", token=assign.token) from None
		except TypeError as ex:
			raise self._create_error(f"{ex} in {self._element.__class__.__name__}", token=assign.token) from None
		except CircularReferenceError as ex:
			paths = "\n".join(" -> ".join(map(attrgetter("name"), path)) for path in ex.paths)
			raise self._create_error(f"{ex} in {self._element.__class__.__name__}", after=f"Paths:\n{paths}", token=assign.token) from None

		return None

	def _build_MemberAccess(self, member_access):
		value = self._build(member_access.value)
		member = member_access.member

		value = value.eval()

		assert isinstance(value, Element)
		assert isinstance(member, Name)

		return self._get_property(value, member.name, token=member_access.token)

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
		elif unit in (unit.value for unit in AngleUnit):
			return Angle(value, AngleUnit(unit))
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

	def _build_Name(self, name):
		assert len(name.children) == 0
		return self._get_property(self._element, name.name, token=name.token)
