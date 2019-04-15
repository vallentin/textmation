#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps

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


@function((Number, Number, Number), Vec3)
def rgb(r, g, b):
	return Vec3(r.value, g.value, b.value)


@function((Number, Number, Number, Number), Vec4)
def rgba(r, g, b, a):
	return Vec4(r.value, g.value, b.value, a.value)
