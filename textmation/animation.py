#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import islice, repeat, starmap
from functools import total_ordering
import bisect
from enum import IntEnum


def normalize(value, lower, upper):
	return (value - lower) / (upper - lower)


def lerp(a, b, t):
	# return a + t * (b - a) # Imprecise
	return (1 - t) * a + t * b # Precise


def remap(value, lower1, upper1, lower2, upper2):
	# return lower2 + (upper2 - lower2) * ((value - lower1) / (upper1 - lower1))
	return lerp(lower2, upper2, normalize(value, lower1, upper1))


def ping_pong(value, lower=0, upper=1):
	length = upper - lower
	length2 = length * 2
	ping_ponged = value % length2

	if ping_ponged < 0:
		ping_ponged = -ping_ponged

	if ping_ponged >= length:
		return lower + length2 - ping_ponged
	else:
		return lower + ping_ponged


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


class AnimationFillMode(IntEnum):
	Never = 1
	After = 2
	Before = 3
	Always = 4
	Default = Never


class AnimationDirection(IntEnum):
	Normal = 1
	Reverse = 2
	Alternate = 3
	AlternateReverse = 4
	Default = Normal


Infinite = object()


class Animation:
	def __init__(self, property=None):
		self.keyframes = []
		self.property = property
		self.delay = 0
		self.iterations = 1.0
		self.direction = AnimationDirection.Default
		self.fill_mode = AnimationFillMode.Default

	@property
	def begin_time(self):
		return self.keyframes[0].time + self.delay

	@property
	def end_time(self):
		if self.iterations is Infinite:
			return self.begin_time
		return self.begin_time + self.iteration_duration * self.iterations

	@property
	def duration(self):
		return self.end_time - self.begin_time

	@property
	def iteration_duration(self):
		first = self.keyframes[0].time
		last  = self.keyframes[-1].time
		duration = last - first
		return duration

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
		time = max(time - self.delay, 0)

		if self.iterations is not Infinite:
			time = min(time, self.end_time)

		if self.direction in (AnimationDirection.Normal, AnimationDirection.Reverse):
			time %= self.iteration_duration
		elif self.direction in (AnimationDirection.Alternate, AnimationDirection.AlternateReverse):
			time = ping_pong(time, 0, self.iteration_duration)

		if self.direction in (AnimationDirection.Reverse, AnimationDirection.AlternateReverse):
			time = self.iteration_duration - time

		before, after = self.get_between(time)
		if before == after:
			return before.value

		# return remap(time, before.time, after.time, before.value, after.value)

		t = normalize(time, before.time, after.time)
		return lerp_value(before.value, after.value, t)

	def is_affecting(self, time):
		if self.fill_mode == AnimationFillMode.Always:
			return True

		if self.iterations is Infinite:
			return time >= self.begin_time

		if self.fill_mode != AnimationFillMode.Never:
			return self.begin_time <= time <= self.end_time
		if self.fill_mode != AnimationFillMode.After:
			return time >= self.begin_time
		if self.fill_mode != AnimationFillMode.Before:
			return time <= self.end_time

		return False


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
