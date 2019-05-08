#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager
import math
import re

from .lexer import Lexer, TokenType


_keywords = "create", "as", "template", "inherit", "include"
_literals = "true", "false", "infinite"
_units    = "%", "px", "s", "ms", "deg", "rad", "turn"


class Node:
	def __init__(self, children=None, *, token=None):
		self.children = []
		self.token = token
		if children is not None:
			self.extend(children)

	def add(self, node):
		assert isinstance(node, Node)
		self.children.append(node)

	def extend(self, iterable):
		for item in iterable:
			self.add(item)

	def __repr__(self):
		return f"<{self.__class__.__name__}>"


class Include(Node):
	def __init__(self, path, *, token=None):
		super().__init__(token=token)
		self.path = path

	def __repr__(self):
		# return f"<{self.__class__.__name__}: {self.path}>"
		return f"<{self.__class__.__name__}: {'.'.join(self.path)}>"


class Create(Node):
	def __init__(self, element, name=None, *, token=None):
		super().__init__(token=token)
		self.element = element
		self.name = name

	def __repr__(self):
		if self.name is not None:
			return f"<{self.__class__.__name__}: {self.element}, {self.name}>"
		else:
			return f"<{self.__class__.__name__}: {self.element}>"


class Scene(Create):
	def __init__(self, name=None, *, token=None):
		super().__init__("Scene", name=name, token=token)


class Template(Node):
	def __init__(self, name, inherit, *, token=None):
		super().__init__(token=token)
		self.name = name
		self.inherit = inherit

	def __repr__(self):
		if self.inherit is not None:
			return f"<{self.__class__.__name__}: {self.name}, {self.inherit}>"
		else:
			return f"<{self.__class__.__name__}: {self.name}>"


class Name(Node):
	def __init__(self, name, *, token=None):
		super().__init__(token=token)
		self.name = name

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.name}>"


class Number(Node):
	def __init__(self, value, *, token=None):
		super().__init__(token=token)

		if not isinstance(value, (int, float)):
			m = re.match(r"^(\d+(?:\.\d+)?)(.+)?$", value)
			if m is None:
				raise ParserError(f"Invalid number format {value!r}")

			self.value, self.unit = m.groups()
			self.value = float(self.value) if "." in self.value else int(self.value)
		else:
			self.value = value
			self.unit = None

		if self.unit is not None:
			if self.unit not in _units:
				raise ParserError(f"Unexpected unit {self.unit!r}, expected any of {_units}")

	def __repr__(self):
		if self.unit is not None:
			return f"<{self.__class__.__name__}: {self.value}{self.unit}>"
		else:
			return f"<{self.__class__.__name__}: {self.value}>"


class String(Node):
	def __init__(self, string, *, token=None):
		super().__init__(token=token)
		self.string = string

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.string!r}>"


class UnaryOp(Node):
	def __init__(self, op, operand, *, token=None):
		super().__init__([operand], token=token)
		self.op = op

	@property
	def operand(self):
		return self.children[0]

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.op!r}>"


class BinOp(Node):
	def __init__(self, op, lhs, rhs, *, token=None):
		super().__init__([lhs, rhs], token=token)
		self.op = op

	@property
	def lhs(self):
		return self.children[0]

	@property
	def rhs(self):
		return self.children[1]

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.op!r}>"


class Define(Node):
	def __init__(self, name, value, *, token=None):
		super().__init__([name, value], token=token)

	@property
	def name(self):
		return self.children[0]

	@property
	def value(self):
		return self.children[1]


class Assign(Node):
	def __init__(self, name, value, *, token=None):
		super().__init__([name, value], token=token)

	@property
	def name(self):
		return self.children[0]

	@property
	def value(self):
		return self.children[1]


class MemberAccess(Node):
	def __init__(self, value, member, *, token=None):
		super().__init__([value, member], token=token)

	@property
	def value(self):
		return self.children[0]

	@property
	def member(self):
		return self.children[1]


class Call(Node):
	def __init__(self, name, args, *, token=None):
		super().__init__(args, token=token)
		assert isinstance(name, str)
		self.name = name

	@property
	def args(self):
		return self.children

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.name}>"


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
			return ParserError("%s at %d:%d to %d:%d" % (message, *begin, *end))
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
			if value is not None:
				raise ParserError("Unexpected %r, expected %r at %d:%d to %d:%d" % (token.value, value, *begin, *end))
			else:
				raise ParserError("Unexpected %r, expected %s at %d:%d to %d:%d" % (token.value, type.name, *begin, *end))

		if value is not None:
			if isinstance(value, tuple):
				if token.value not in value:
					begin, end = token.span
					value = " or ".join(map(repr, value))
					raise ParserError("Unexpected %r, expected %s at %d:%d to %d:%d" % (token.value, value, *begin, *end))
			else:
				if token.value != value:
					begin, end = token.span
					raise ParserError("Unexpected %r, expected %r at %d:%d to %d:%d" % (token.value, value, *begin, *end))

		return token

	def _next_name(self):
		token = self._expect_token(TokenType.Identifier)
		name = token.value
		if name in _keywords:
			self._fail(f"Unexpected keyword {name!r}", token=token)
		return name

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
		# scene = Create("Scene")
		# scene = Create("Scene", token=self._peek())
		scene = Scene()
		scene.extend(self._parse_body_elements(allow_template=True))
		return scene

	def _parse_include(self):
		token = self._expect_token(TokenType.Identifier, "include")

		path = [self._next_name()]
		while self._next_if(TokenType.Symbol, "."):
			path.append(self._next_name())

		return Include(path, token=token)

	def _parse_create(self):
		self._expect_token(TokenType.Identifier, "create")

		token = self._peek()
		element_type = self._next_name()

		name = None
		if self._next_if(TokenType.Identifier, "as"):
			name = self._next_name()

		create = Create(element_type, name, token=token)
		create.extend(self._parse_body())

		return create

	def _parse_template(self):
		self._expect_token(TokenType.Identifier, "template")

		token = self._peek()
		name = self._next_name()

		inherit = None
		if self._next_if(TokenType.Identifier, "inherit"):
			inherit = self._next_name()

		template = Template(name, inherit, token=token)
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
					self._fail("Template not allowed", token=self._peek())
				body.append(self._parse_template())
			elif self._peek_if(TokenType.Identifier, "include"):
				if not allow_template:
					self._fail("Include not allowed", token=self._peek())
				body.append(self._parse_include())
			elif self._peek_if(TokenType.Identifier):
				body.append(self._parse_assignment())
			else:
				break
		return body

	def _parse_assignment(self):
		name = self._parse_lvalue()
		token = self._expect_token(TokenType.Symbol, ("=", ":="))
		value = self._parse_rvalue()
		if token.value == ":=":
			return Define(name, value, token=token)
		else:
			return Assign(name, value, token=token)

	def _parse_lvalue(self):
		token = self._peek()
		name = self._next_name()
		if name in _literals:
			self._fail(f"Unexpected literal {name!r}, expected {TokenType.Identifier.name}", token=token)
		return Name(name, token=token)

	def _parse_rvalue(self):
		return self._parse_bitwise_or()

	def _parse_bitwise_or(self):
		result = self._parse_additive()
		while self._peek_if(TokenType.Symbol, "|"):
			token = self._next()
			result = BinOp(token.value, result, self._parse_additive(), token=token)
		return result

	def _parse_additive(self):
		result = self._parse_multiplicative()
		while self._peek_if(TokenType.Symbol, ("+", "-")):
			token = self._next()
			result = BinOp(token.value, result, self._parse_multiplicative(), token=token)
		return result

	def _parse_multiplicative(self):
		result = self._parse_unary()
		while self._peek_if(TokenType.Symbol, ("*", "/")):
			token = self._next()
			result = BinOp(token.value, result, self._parse_unary(), token=token)
		return result

	def _parse_unary(self):
		if self._peek_if(TokenType.Symbol, ("-", "+")):
			token = self._next()
			return UnaryOp(token.value, self._parse_unary(), token=token)
		else:
			return self._parse_value()

	def _parse_value(self):
		if self._peek_if(TokenType.Identifier):
			token = self._peek()
			name = Name(self._next_name(), token=token)

			if name.name == "true":
				return Number(1)
			elif name.name == "false":
				return Number(0)
			elif name.name == "infinite":
				return Number(math.inf)

			if name in _literals:
				self._fail(f"Unexpected literal {name!r}, expected {TokenType.Identifier.name}", token=token)

			if self._next_if(TokenType.Symbol, "("):
				args = []

				self._skip_newlines()
				if not self._next_if(TokenType.Symbol, ")"):
					while True:
						self._skip_newlines()
						args.append(self._parse_rvalue())

						self._skip_newlines()
						if self._next_if(TokenType.Symbol, ")"):
							break

						self._skip_newlines()
						self._expect_token(TokenType.Symbol, ",")

				return Call(name.name, args)

			while True:
				token = self._peek()
				if not self._next_if(TokenType.Symbol, "."):
					break

				next_name_token = self._peek()
				next_name = self._next_name()
				if next_name in _literals:
					self._fail(f"Unexpected literal {next_name!r}, expected {TokenType.Identifier.name}", token=next_name_token)

				name = MemberAccess(name, Name(next_name, token=next_name_token), token=token)

			return name
		elif self._peek_if(TokenType.Number):
			token = self._next()
			try:
				return Number(token.value, token=token)
			except ParserError as ex:
				raise self._create_error(str(ex), token=token) from None
		elif self._peek_if(TokenType.String):
			token = self._next()
			return String(token.value, token=token)
		elif self._peek_if(TokenType.Symbol, "("):
			self._expect_token(TokenType.Symbol, "(")
			value = self._parse_rvalue()
			self._expect_token(TokenType.Symbol, ")")
			return value
		else:
			self._unexpected()


def parse(string):
	return Parser().parse(string)
