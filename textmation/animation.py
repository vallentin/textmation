#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import islice, repeat, starmap
from functools import total_ordering
import bisect


def normalize(value, lower, upper):
	return (value - lower) / (upper - lower)


def lerp(a, b, t):
	# return a + t * (b - a) # Imprecise
	return (1 - t) * a + t * b # Precise


def remap(value, lower1, upper1, lower2, upper2):
	# return lower2 + (upper2 - lower2) * ((value - lower1) / (upper1 - lower1))
	return lerp(lower2, upper2, normalize(value, lower1, upper1))


def lerp_tuple(a, b, t):
	try:
		return lerp(a, b, t)
	except TypeError:
		pass

	assert isinstance(a, tuple)
	assert isinstance(b, tuple)
	assert len(a) == len(b)

	return tuple(starmap(lerp, zip(a, b, repeat(t))))


def lerp_value(a, b, t):
	try:
		return lerp_tuple(a, b, t)
	except AssertionError:
		return type(a).lerp(a, b, t)


class Animation:
	def __init__(self, property=None):
		self.keyframes = []
		self.property = property
		self.delay = 0

	@property
	def begin_time(self):
		return self.keyframes[0].time + self.delay

	@property
	def end_time(self):
		return self.keyframes[-1].time + self.delay

	@property
	def duration(self):
		return self.end_time - self.begin_time

	def add(self, keyframe):
		# self.keyframes.append(keyframe)
		# self.keyframes.sort()
		bisect.insort(self.keyframes, keyframe)

	def add_all(self, keyframes):
		for keyframe in keyframes:
			self.add(keyframe)

	def get_between(self, time):
		assert len(self.keyframes) > 0

		first = self.keyframes[0]
		if time < first.time:
			return first, first

		last = self.keyframes[-1]
		if time >= last.time:
			return last, last

		# index = bisect.bisect_left(self.keyframes, Keyframe(time, None))

		for i, keyframe in enumerate(islice(self.keyframes, 1, None), start=1):
			if time < keyframe.time:
				return self.keyframes[i - 1], keyframe

		assert False

	def get_value(self, time):
		time -= self.delay

		before, after = self.get_between(time)
		if before == after:
			return before.value

		# return remap(time, before.time, after.time, before.value, after.value)

		t = normalize(time, before.time, after.time)
		return lerp_value(before.value, after.value, t)


@total_ordering
class Keyframe:
	def __init__(self, time, value):
		self._time = time
		self.value = value

	@property
	def time(self):
		return self._time

	def __lt__(self, other):
		return self._time < other._time

	def __repr__(self):
		return "<%s: %.2fs, %r>" % (self.__class__.__name__, self.time, self.value)
