#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Reference: https://vallentin.io/2016/11/29/pretty-print-tree

from operator import attrgetter
from io import StringIO


def pretty_duration(seconds):
	seconds = int(seconds)
	days, seconds = divmod(seconds, 86400)
	hours, seconds = divmod(seconds, 3600)
	minutes, seconds = divmod(seconds, 60)
	if days > 0:
		return f"{days}d{hours}h{minutes}m{seconds}s"
	elif hours > 0:
		return f"{hours}h{minutes}m{seconds}s"
	elif minutes > 0:
		return f"{minutes}m{seconds}s"
	else:
		return f"{seconds}s"


def pprint_tree(node, stringify=str, children=attrgetter("children"), file=None, *, _prefix="", _last=True):
	print(_prefix, "`- " if _last else "|- ", stringify(node), sep="", file=file)
	_prefix += "   " if _last else "|  "
	_children = children(node)
	child_count = len(_children)
	for i, child in enumerate(_children):
		_last = i == (child_count - 1)
		pprint_tree(child, stringify, children, file, _prefix=_prefix, _last=_last)


def pprint_tree_multiline(node, stringify=str, children=attrgetter("children"), file=None, *, _prefix="", _last=True):
	string = stringify(node).strip()
	line, lines = string.partition("\n")[0::2]

	print(_prefix, "`- " if _last else "|- ", line, sep="", file=file)

	_prefix += "   " if _last else "|  "

	if lines:
		for line in lines.splitlines():
			print(_prefix, line, sep="", file=file)

	_children = children(node)
	child_count = len(_children)
	for i, child in enumerate(_children):
		_last = i == (child_count - 1)
		pprint_tree_multiline(child, stringify, children, file, _prefix=_prefix, _last=_last)


def pprint_ast(node, file=None):
	pprint_tree(node, file=file)


def pprint_element_properties(element, file=None):
	max_name_length = 0
	for name, property in element.properties.items():
		types = " | ".join(map(attrgetter("name"), property.types))
		name = f"{name}: {types}"
		max_name_length = max(max_name_length, len(name))

	for name, property in element.properties.items():
		types = " | ".join(map(attrgetter("name"), property.types))
		name = f"{name}: {types}".ljust(max_name_length)
		value = property.eval().unbox()

		print(f"{name} = {value!r}", file=file)


def _stringify_element(element):
	with StringIO() as f:
		print(element, file=f)
		pprint_element_properties(element, file=f)
		return f.getvalue()


def pprint_element(element, file=None):
	pprint_tree_multiline(element, _stringify_element, file=file)
