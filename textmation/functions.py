#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
import builtins
import math
import colorsys

from .datatypes import *


functions = {}


class FunctionError(Exception):
	pass


def type_check_function_call(f, args):
	name = f.name
	parameter_types = f.parameter_types

	if len(parameter_types) != len(args):
		raise TypeError(f"{name} expected {len(parameter_types)} arguments, received {len(args)}")

	for i, (param_type, arg) in enumerate(zip(parameter_types, args), start=1):
		assert isinstance(arg, Value)
		if arg.type is not param_type:
			raise TypeError(f"{name} expected parameter {i} as {param_type.name}, received {arg.type.name}")


def function(*args):
	name, parameter_types, return_type = None, (), None

	assert 1 <= len(args) <= 3
	if len(args) == 1:
		return_type, = args
	elif len(args) == 2:
		parameter_types, return_type = args
	elif len(args) == 3:
		name, parameter_types, return_type = args

	assert name is None or isinstance(name, str)
	assert return_type is not None

	parameter_types = tuple(type if isinstance(type, Type) else type.type for type in parameter_types)

	if not isinstance(return_type, Type):
		return_type = return_type.type

	assert all(isinstance(type, Type) for type in parameter_types)
	assert isinstance(return_type, Type)

	def decorator(f):
		nonlocal name
		if name is None:
			name = f.__name__

		@wraps(f)
		def wrapper(*args):
			type_check_function_call(wrapper, args)

			result = f(*args)

			if not isinstance(result, Value):
				raise FunctionError(f"Expected {return_type.name} from {name}, received {type(result)}")
			if result.type is not return_type:
				raise FunctionError(f"Expected {return_type.name} from {name}, received {result.type.name}")

			return result

		wrapper.name = name
		wrapper.parameter_types = parameter_types
		wrapper.return_type = return_type
		wrapper.type_check = lambda args: type_check_function_call(wrapper, args)

		functions[name] = wrapper

		return wrapper
	return decorator


@function((Number, Number), Number)
def mod(a, b):
	return Number(a.value % b.value)


@function((Number, Number), Number)
def min(a, b):
	return Number(builtins.min(a.value, b.value))


@function((Number, Number), Number)
def max(a, b):
	return Number(builtins.max(a.value, b.value))


@function((Number,), Number)
def floor(x):
	return Number(math.floor(x.value))


@function((Number,), Number)
def ceil(x):
	return Number(math.ceil(x.value))


@function((Number,), Number)
def round(x):
	return Number(builtins.round(x.value))


@function((Number, Number, Number), Color)
def rgb(r, g, b):
	return Color(r.value, g.value, b.value)


@function((Number, Number, Number, Number), Color)
def rgba(r, g, b, a):
	return Color(r.value, g.value, b.value, a.value)


@function((Number, Number, Number), Color)
def hsl(h, s, l):
	r, g, b = colorsys.hls_to_rgb(h.value, l.value, s.value)

	r *= 255
	g *= 255
	b *= 255

	return Color(r, g, b)


@function((Number, Number, Number, Number), Color)
def hsla(h, s, l, a):
	r, g, b = colorsys.hls_to_rgb(h.value, l.value, s.value)

	r *= 255
	g *= 255
	b *= 255
	a = a.value

	return Color(r, g, b, a)
