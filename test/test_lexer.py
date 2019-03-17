#!/usr/bin/env python
# -*- coding: utf-8 -*-

from textwrap import dedent
from unittest import TestCase

from lexer import Lexer, Token, TokenType, LexerError


class LexerTest(TestCase):
	def assertTokenType(self, actual, expected):
		if isinstance(actual, Token):
			actual = actual.type
		if isinstance(expected, Token):
			expected = expected.type
		self.assertEqual(actual, expected)

	def assertTokenValue(self, actual, expected):
		if isinstance(actual, Token):
			actual = actual.value
		if isinstance(expected, Token):
			expected = expected.value
		self.assertEqual(actual, expected)

	def assertTokenSpan(self, actual, expected):
		if isinstance(actual, Token):
			actual = actual.span
		if isinstance(expected, Token):
			expected = expected.span
		self.assertEqual(actual, expected)

	def assertToken(self, actual, *expected):
		assert 1 <= len(expected) <= 3
		if len(expected) == 1:
			expected, = expected
			if not isinstance(expected, Token):
				expected = Token(expected, None)
		else:
			expected = Token(*expected)

		self.assertTokenType(actual, expected)
		if expected.value is not None:
			self.assertTokenValue(actual, expected)
		if expected.span is not None:
			self.assertTokenSpan(actual, expected)

	def test_empty(self):
		string = ""
		with self.subTest(string=string):
			lexer = Lexer(string)
			self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((1, 1), (1, 1)))
			self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((1, 1), (1, 1)))
			self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((1, 1), (1, 1)))

		string = "  "
		with self.subTest(string=string):
			lexer = Lexer(string)
			self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((1, 3), (1, 3)))

		string = "\n"
		with self.subTest(string=string):
			lexer = Lexer(string)
			self.assertToken(lexer.next(), TokenType.Newline, "\n", ((1, 1), (2, 1)))
			self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((2, 1), (2, 1)))

		string = "\r\n"
		with self.subTest(string=string):
			lexer = Lexer(string)
			self.assertToken(lexer.next(), TokenType.Newline, "\r\n", ((1, 1), (2, 1)))
			self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((2, 1), (2, 1)))

		string = "  \t\n"
		with self.subTest(string=string):
			lexer = Lexer(string)
			self.assertToken(lexer.next(), TokenType.Newline, "\n", ((1, 4), (2, 1)))
			self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((2, 1), (2, 1)))

		string = "  \t\r\n"
		with self.subTest(string=string):
			lexer = Lexer(string)
			self.assertToken(lexer.next(), TokenType.Newline, "\r\n", ((1, 4), (2, 1)))
			self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((2, 1), (2, 1)))

		string = "\n\t  "
		with self.subTest(string=string):
			lexer = Lexer(string)
			self.assertToken(lexer.next(), TokenType.Newline, "\n", ((1, 1), (2, 1)))
			self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((2, 4), (2, 4)))

		string = "\r\n\t  "
		with self.subTest(string=string):
			lexer = Lexer(string)
			self.assertToken(lexer.next(), TokenType.Newline, "\r\n", ((1, 1), (2, 1)))
			self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((2, 4), (2, 4)))

		string = "\n\n"
		with self.subTest(string=string):
			lexer = Lexer(string)
			self.assertToken(lexer.next(), TokenType.Newline, "\n", ((1, 1), (2, 1)))
			self.assertToken(lexer.next(), TokenType.Newline, "\n", ((2, 1), (3, 1)))
			self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((3, 1), (3, 1)))

		string = "\r\n\r\n"
		with self.subTest(string=string):
			lexer = Lexer(string)
			self.assertToken(lexer.next(), TokenType.Newline, "\r\n", ((1, 1), (2, 1)))
			self.assertToken(lexer.next(), TokenType.Newline, "\r\n", ((2, 1), (3, 1)))
			self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((3, 1), (3, 1)))

	def test_indentation(self):
		string = dedent("""\
		A
			B
				C
			D
				E
		
		F
			G
			H
		""")

		lexer = Lexer(string)
		self.assertToken(lexer.next(), TokenType.Identifier, "A", ((1, 1), (1, 2)))
		self.assertToken(lexer.next(), TokenType.Newline, "\n", ((1, 2), (2, 1)))

		self.assertToken(lexer.next(), TokenType.Indent, "\t", ((2, 1), (2, 2)))
		self.assertToken(lexer.next(), TokenType.Identifier, "B", ((2, 2), (2, 3)))
		self.assertToken(lexer.next(), TokenType.Newline, "\n", ((2, 3), (3, 1)))

		self.assertToken(lexer.next(), TokenType.Indent, "\t\t", ((3, 1), (3, 3)))
		self.assertToken(lexer.next(), TokenType.Identifier, "C", ((3, 3), (3, 4)))
		self.assertToken(lexer.next(), TokenType.Newline, "\n", ((3, 4), (4, 1)))
		self.assertToken(lexer.next(), TokenType.Dedent, "\t", ((4, 1), (4, 2)))

		self.assertToken(lexer.next(), TokenType.Identifier, "D", ((4, 2), (4, 3)))
		self.assertToken(lexer.next(), TokenType.Newline, "\n", ((4, 3), (5, 1)))

		self.assertToken(lexer.next(), TokenType.Indent, "\t\t", ((5, 1), (5, 3)))
		self.assertToken(lexer.next(), TokenType.Identifier, "E", ((5, 3), (5, 4)))
		self.assertToken(lexer.next(), TokenType.Newline, "\n", ((5, 4), (6, 1)))
		self.assertToken(lexer.next(), TokenType.Newline, "\n", ((6, 1), (7, 1)))
		self.assertToken(lexer.next(), TokenType.Dedent, "\t", ((7, 1), (7, 1)))
		self.assertToken(lexer.next(), TokenType.Dedent, "", ((7, 1), (7, 1)))

		self.assertToken(lexer.next(), TokenType.Identifier, "F", ((7, 1), (7, 2)))
		self.assertToken(lexer.next(), TokenType.Newline, "\n", ((7, 2), (8, 1)))

		self.assertToken(lexer.next(), TokenType.Indent, "\t", ((8, 1), (8, 2)))
		self.assertToken(lexer.next(), TokenType.Identifier, "G", ((8, 2), (8, 3)))
		self.assertToken(lexer.next(), TokenType.Newline, "\n", ((8, 3), (9, 1)))

		self.assertToken(lexer.next(), TokenType.Identifier, "H", ((9, 2), (9, 3)))
		self.assertToken(lexer.next(), TokenType.Newline, "\n", ((9, 3), (10, 1)))
		self.assertToken(lexer.next(), TokenType.Dedent, "", ((10, 1), (10, 1)))
		self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((10, 1), (10, 1)))

	def test_indentation_inconsistent_invalid(self):
		strings = [
			dedent("""\
			A
				B
			    C
			"""),
			dedent("""\
			A
				B
					C
					D
				E
					F
				    G
			"""),
		]

		for string in strings:
			with self.subTest(string=string):
				lexer = Lexer(string)
				with self.assertRaisesRegex(LexerError, r"^Inconsistent use of tabs and spaces in indentation \(\d+:\d+, \d+:\d+\)$"):
					for _ in lexer:
						pass

	def test_indentation_inconsistent_valid(self):
		strings = [
			dedent("""\
			A
			    # Test
				B
			"""),
			dedent("""\
			A
				B
					C
					D
				E
				    F
				    G
			"""),
		]

		for string in strings:
			with self.subTest(string=string):
				lexer = Lexer(string)
				for _ in lexer:
					pass

	def test_identifier(self):
		identifiers = [
			"x",
			"_x",
			"xyz",
			"xyz123",
		]

		for identifier in identifiers:
			with self.subTest(identifier=identifier):
				lexer = Lexer(identifier)
				self.assertToken(lexer.next(), TokenType.Identifier, identifier, ((1, 1), (1, len(identifier) + 1)))
				self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((1, len(identifier) + 1), (1, len(identifier) + 1)))

	def test_string(self):
		strings = [
			'"Hello World"',
			'"Hello \\" World"',
			'"Hello \\\' World"',
			'"Hello \' World"',

			"'Hello World'",
			"'Hello \\' World'",
			"'Hello \\\" World'",
			"'Hello \" World'",
		]

		for string in strings:
			with self.subTest(string=string):
				lexer = Lexer(string)
				self.assertToken(lexer.next(), TokenType.String, string, ((1, 1), (1, len(string) + 1)))
				self.assertToken(lexer.next(), TokenType.EndOfStream, "", ((1, len(string) + 1), (1, len(string) + 1)))

	def test_string_unterminated_eos(self):
		strings = [
			'"Hello World',
			'"Hello World\\"',
			'"Hello World\'',

			"'Hello World",
			"'Hello World\\'",
			"'Hello World\"",
		]

		for string in strings:
			with self.subTest(string=string):
				lexer = Lexer(string)
				with self.assertRaisesRegex(LexerError, r"Unexpected end of stream"):
					lexer.next()

	def test_string_unterminated_eol(self):
		strings = [
			'"Hello World\n',
			'"Hello World\\"\n',
			'"Hello World\'\n',

			"'Hello World\n",
			"'Hello World\\'\n",
			"'Hello World\"\n",
		]

		for string in strings:
			with self.subTest(string=string):
				lexer = Lexer(string)
				with self.assertRaisesRegex(LexerError, r"^Unexpected end of line while scanning string literal \(\d+:\d+, \d+:\d+\)$"):
					lexer.next()
