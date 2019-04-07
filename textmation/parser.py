#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager
import re

from .lexer import Lexer, TokenType


_units = "%", "px", "s", "ms"


def pprint_tree(node, file=None, prefix="", last=True):
	print(prefix, "`- " if last else "|- ", node, sep="", file=file)
	prefix += "   " if last else "|  "
	child_count = len(node.children)
	for i, child in enumerate(node.children):
		last = i == (child_count - 1)
		pprint_tree(child, file, prefix, last)


class Node:
	def __init__(self, children=None):
		if children is None:
			children = []
		self.children = children

	def add(self, node):
		self.children.append(node)

	def extend(self, iterable):
		for item in iterable:
			self.add(item)

	def __repr__(self):
		return f"<{self.__class__.__name__}>"


class Create(Node):
	def __init__(self, element, name=None):
		super().__init__()
		self.element = element
		self.name = name

	def __repr__(self):
		if self.name is not None:
			return f"<{self.__class__.__name__}: {self.element}, {self.name}>"
		else:
			return f"<{self.__class__.__name__}: {self.element}>"


class Template(Node):
	def __init__(self, name, inherit):
		super().__init__()
		self.name = name
		self.inherit = inherit

	def __repr__(self):
		if self.inherit is not None:
			return f"<{self.__class__.__name__}: {self.name}, {self.inherit}>"
		else:
			return f"<{self.__class__.__name__}: {self.name}>"


class Name(Node):
	def __init__(self, name):
		super().__init__()
		self.name = name

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.name}>"


class Number(Node):
	def __init__(self, value):
		super().__init__()

		m = re.match(r"^(\d+(?:\.\d+)?)(.+)?$", value)
		if m is None:
			raise ParserError(f"Invalid number format {value!r}")

		self.string = value
		self.raw_value, self.unit = m.groups()
		self.value = float(self.raw_value) if "." in self.raw_value else int(self.raw_value)

		if self.unit is not None:
			if self.unit not in _units:
				raise ParserError(f"Unexpected unit {self.unit!r}, expected any of {_units}")

	def __repr__(self):
		if self.unit is not None:
			return f"<{self.__class__.__name__}: {self.value}{self.unit}>"
		else:
			return f"<{self.__class__.__name__}: {self.value}>"


class String(Node):
	def __init__(self, string):
		super().__init__()
		self.string = string

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.string!r}>"


class UnaryOp(Node):
	def __init__(self, op, operand):
		super().__init__([operand])
		self.op = op

	@property
	def operand(self):
		return self.children[0]

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.op!r}>"


class BinOp(Node):
	def __init__(self, op, lhs, rhs):
		super().__init__([lhs, rhs])
		self.op = op

	@property
	def lhs(self):
		return self.children[0]

	@property
	def rhs(self):
		return self.children[1]

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.op!r}>"


class Assign(Node):
	def __init__(self, name, value):
		super().__init__([name, value])

	@property
	def name(self):
		return self.children[0]

	@property
	def value(self):
		return self.children[1]


class ParserError(Exception):
	pass


class Parser:
	def __init__(self):
		self._lexer = None

	def _next(self):
		for token in self._lexer:
			if token.type == TokenType.Comment:
				continue
			return token

	def _peek(self, offset=0):
		with self._lexer.peeking():
			for _ in range(offset):
				self._next()
			return self._next()

	def _peek_if(self, type, value=None, offset=0):
		token = self._peek(offset)

		if token.type != type:
			return False

		if value is not None:
			if isinstance(value, tuple):
				return token.value in value
			else:
				return token.value == value

		return True

	def _next_if(self, type, value=None, offset=0):
		result = self._peek_if(type, value, offset)
		if result:
			self._next()
		return result

	def _skip(self, *types):
		with self._lexer.peeking() as p:
			for token in self._lexer:
				if token.type not in types:
					break
				p.save()

	def _skip_newlines(self):
		self._skip(TokenType.Newline, TokenType.Comment)

	@staticmethod
	def _create_error(message, *, span=None, token=None):
		if span is None and token is not None:
			span = token.span

		if span is not None:
			begin, end = span
			return ParserError("%s (%d:%d, %d:%d)" % (message, *begin, *end))
		else:
			return ParserError(message)

	def _fail(self, message, *, span=None, token=None):
		raise self._create_error(message, span=span, token=token)

	def _unexpected(self):
		raise ParserError("Unexpected %s" % self._next())

	def _expect_token(self, type, value=None):
		token = self._next()

		if token.type != type:
			begin, end = token.span
			raise ParserError("Unexpected %s, expected %s (%d:%d, %d:%d)" % (token.type.name, type.name, *begin, *end))

		if value is not None:
			if token.value != value:
				begin, end = token.span
				raise ParserError("Unexpected %r, expected %r (%d:%d, %d:%d)" % (token.value, value, *begin, *end))

		return token

	@contextmanager
	def _indentation(self):
		self._skip_newlines()
		self._expect_token(TokenType.Indent)
		yield
		self._skip_newlines()
		self._expect_token(TokenType.Dedent)

	def parse(self, string):
		self._lexer = Lexer(string)

		scene = self._parse_scene()

		self._skip_newlines()
		self._expect_token(TokenType.EndOfStream)

		self._lexer = None

		return scene

	def _parse_scene(self):
		scene = Create("Scene")
		scene.extend(self._parse_body_elements(allow_template=True))
		return scene

	def _parse_create(self):
		self._expect_token(TokenType.Identifier, "create")

		element_type = self._expect_token(TokenType.Identifier).value

		name = None
		if self._next_if(TokenType.Identifier, "as"):
			name = self._expect_token(TokenType.Identifier).value

		create = Create(element_type, name)
		create.extend(self._parse_body())

		return create

	def _parse_template(self):
		self._expect_token(TokenType.Identifier, "template")

		name = self._expect_token(TokenType.Identifier).value

		inherit = None
		if self._next_if(TokenType.Identifier, "inherit"):
			inherit = self._expect_token(TokenType.Identifier).value

		template = Template(name, inherit)
		template.extend(self._parse_body())

		return template

	def _parse_body(self, *, allow_template=False):
		self._skip_newlines()
		if self._peek_if(TokenType.Indent):
			with self._indentation():
				return self._parse_body_elements(allow_template=allow_template)
		return []

	def _parse_body_elements(self, *, allow_template=False):
		body = []
		while True:
			self._skip_newlines()
			if self._peek_if(TokenType.Identifier, "create"):
				body.append(self._parse_create())
			elif self._peek_if(TokenType.Identifier, "template"):
				if not allow_template:
					self._unexpected()
				body.append(self._parse_template())
			elif self._peek_if(TokenType.Identifier):
				body.append(self._parse_assignment())
			else:
				break
		return body

	def _parse_assignment(self):
		name = self._parse_lvalue()
		self._expect_token(TokenType.Symbol, "=")
		value = self._parse_rvalue()
		return Assign(name, value)

	def _parse_lvalue(self):
		name = self._expect_token(TokenType.Identifier).value
		return Name(name)

	def _parse_rvalue(self):
		return self._parse_additive()

	def _parse_additive(self):
		result = self._parse_multiplicative()
		while self._peek_if(TokenType.Symbol, ("+", "-")):
			result = BinOp(self._next().value, result, self._parse_multiplicative())
		return result

	def _parse_multiplicative(self):
		result = self._parse_unary()
		while self._peek_if(TokenType.Symbol, ("*", "/")):
			result = BinOp(self._next().value, result, self._parse_unary())
		return result

	def _parse_unary(self):
		if self._peek_if(TokenType.Symbol, ("-", "+")):
			return UnaryOp(self._next().value, self._parse_unary())
		else:
			return self._parse_value()

	def _parse_value(self):
		if self._peek_if(TokenType.Identifier):
			return Name(self._next().value)
		elif self._peek_if(TokenType.Number):
			token = self._next()
			try:
				return Number(token.value)
			except ParserError as ex:
				raise self._create_error(str(ex), token=token) from None
		elif self._peek_if(TokenType.String):
			return String(self._next().value)
		elif self._peek_if(TokenType.Symbol, "("):
			self._expect_token(TokenType.Symbol, "(")
			value = self._parse_rvalue()
			self._expect_token(TokenType.Symbol, ")")
			return value
		else:
			self._unexpected()


def parse(string):
	return Parser().parse(string)
