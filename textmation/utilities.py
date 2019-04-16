#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import reduce


_sentinel = object()


def getattr_consecutive(obj, name, default=_sentinel):
	try:
		return reduce(getattr, name.split("."), obj)
	except AttributeError as e:
		if default is _sentinel:
			raise e from None
		return default


def setattr_consecutive(obj, name, value):
	names, name = name.rpartition(".")[0::2]
	if names:
		obj = getattr_consecutive(obj, names)
	assert hasattr(obj, name)
	setattr(obj, name, value)


def iter_all_subclasses(cls):
	# Assumes no multiple inheritance
	for cls in cls.__subclasses__():
		yield cls
		yield from iter_all_subclasses(cls)
