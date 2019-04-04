#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
import time
import os

from textmation import *


def render_example(scene):
	scene.reset()

	print(f"Rendering {calc_frame_count(scene.duration, scene.frame_rate, inclusive=True)} frames...")

	frames = render_animation(scene, inclusive=True)

	print("Exporting Frames...")

	os.makedirs("output", exist_ok=True)

	for i, frame in enumerate(frames, start=1):
		filename = "output/frame_%04d.png" % i
		frame.save(filename)

	print("Exporting GIF...")

	Image.save_gif("output.gif", frames, scene.frame_rate)


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
