#!/usr/bin/env python
# -*- coding: utf-8 -*-


def pprint_tree(node, file=None, *, _prefix="", _last=True):
	print(_prefix, "`- " if _last else "|- ", node, sep="", file=file)
	_prefix += "   " if _last else "|  "
	child_count = len(node.children)
	for i, child in enumerate(node.children):
		_last = i == (child_count - 1)
		pprint_tree(child, file, _prefix=_prefix, _last=_last)


def pprint_ast(node, file=None):
	pprint_tree(node, file)
