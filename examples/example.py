#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
import time


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


def timeit(message="Rendered in {duration}"):
	def decorator(f):
		@wraps(f)
		def wrapper(*args, **kwargs):
			begin = time.time()
			result = f(*args, **kwargs)
			end = time.time()
			duration = end - begin
			print(message.format(duration=pretty_duration(duration)))
			return result
		return wrapper
	return decorator
