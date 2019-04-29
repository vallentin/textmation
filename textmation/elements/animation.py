#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import islice
from functools import total_ordering
from math import isinf
from enum import IntEnum

from ..datatypes import Time, TimeUnit, register_enum
from .element import Element, ElementError


def is_int(x):
	if isinstance(x, int):
		return True
	return x.is_integer()


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


@register_enum
class AnimationDirection(IntEnum):
	Normal           = 1
	Reverse          = 2
	Alternate        = 3
	AlternateReverse = 4
	Default          = Normal


@register_enum
class AnimationFillMode(IntEnum):
	Never   = 1
	After   = 2
	Before  = 3
	Always  = 4
	Default = Never


class Animation(Element):
	def __init__(self):
		super().__init__()
		self.element_properties = None
		self.keyframes = []
		# self._duration = Time(0, TimeUnit.Seconds)

	def on_ready(self):
		super().on_ready()

		# self.define("duration", self._duration, constant=True)

		self.define("delay", Time(0, TimeUnit.Seconds), constant=True)

		self.define("iterations", 1, constant=True)

		self.define("direction", AnimationDirection.Default, constant=True)
		self.define("fill_mode", AnimationFillMode.Default, constant=True)

	def on_created(self):
		super().on_created()

		self.keyframes.sort()

		if len(self.keyframes) < 1:
			raise ElementError(f"{self.__class__.__name__} requires at least one keyframe")

		# Only calculate duration if it wasn't manually set
		# if self._duration is self.get("duration").get():
		# 	self.set("duration", max(self.keyframes).p_time)

		self.element_properties = set()
		for keyframe in self.keyframes:
			self.element_properties.update(keyframe.element_properties)

		for keyframe in self.keyframes:
			for name in self.element_properties:
				if name in keyframe.element_properties:
					continue
				keyframe.set(name, self.element.get(name).get())
				# TODO: Check if the property value can be interpolated

	def compute(self, time):
		super().compute(time)

		if not self.is_affecting(time):
			return

		time = max(time - self.p_delay.seconds, 0)

		is_after = not self.infinite_iterations and time >= self.duration

		if not self.infinite_iterations:
			time = min(time, self.duration)

		if self.direction in (AnimationDirection.Normal, AnimationDirection.Reverse):
			time %= self.iteration_duration
			if self.direction == AnimationDirection.Reverse:
				time = self.iteration_duration - time
		elif self.direction == AnimationDirection.Alternate:
			time = ping_pong(time, 0, self.iteration_duration)
		elif self.direction == AnimationDirection.AlternateReverse:
			time = ping_pong(time + self.iteration_duration, 0, self.iteration_duration)

		before, after = self.get_between(time)

		if is_after and is_int(self.iterations):
			if self.fill_mode in (AnimationFillMode.After, AnimationFillMode.Always):
				if self.direction == AnimationDirection.Normal:
					after = self.keyframes[-1]
					before = after
				elif self.direction == AnimationDirection.Reverse:
					after = self.keyframes[0]
					before = after

		if before == after:
			for name in self.element_properties:
				self.element.set_computed(name, before.eval(name))
		else:
			time = normalize(time, before.time.seconds, after.time.seconds)

			for name in self.element_properties:
				before_value = before.eval(name)
				after_value = after.eval(name)
				self.element.set_computed(name, lerp(before_value, after_value, time))

	def add(self, keyframe):
		super().add(keyframe)

		if isinstance(keyframe, Keyframe):
			self.keyframes.append(keyframe)
		else:
			raise NotImplementedError

	@property
	def element(self):
		return self.parent

	@property
	def duration(self):
		# return self.p_duration.seconds
		return self.end_time - self.begin_time

	@property
	def begin_time(self):
		return (self.keyframes[0].time + self.p_delay).seconds

	@property
	def end_time(self):
		# return self.begin_time + self.duration
		iterations = self.p_iterations
		if isinf(iterations):
			return self.begin_time
		return self.begin_time + self.iteration_duration * iterations

	@property
	def iteration_duration(self):
		first = self.keyframes[0].time.seconds
		last  = self.keyframes[-1].time.seconds
		duration = last - first
		return duration

	@property
	def iterations(self):
		return self.p_iterations

	@property
	def infinite_iterations(self):
		return isinf(self.iterations)

	@property
	def direction(self):
		return self.p_direction

	@property
	def fill_mode(self):
		return self.p_fill_mode

	def get_between(self, time):
		first = self.keyframes[0]
		if time < first.time.seconds:
			return first, first

		last = self.keyframes[-1]
		if time >= last.time.seconds:
			return last, last

		for i, keyframe in enumerate(islice(self.keyframes, 1, None), start=1):
			if time < keyframe.time.seconds:
				return self.keyframes[i - 1], keyframe

	def is_affecting(self, time):
		if self.fill_mode == AnimationFillMode.Always:
			return True

		if self.infinite_iterations:
			return time >= self.begin_time

		if self.fill_mode == AnimationFillMode.Never:
			return self.begin_time <= time <= self.end_time
		if self.fill_mode == AnimationFillMode.After:
			return time >= self.begin_time
		if self.fill_mode == AnimationFillMode.Before:
			return time <= self.end_time

		return False


@total_ordering
class Keyframe(Element):
	def __init__(self):
		super().__init__()
		self.element_properties = []

	def on_ready(self):
		super().on_ready()

		self.define("time", Time(0, TimeUnit.Seconds), constant=True)

	def compute(self, time):
		# Keyframe is transparently setting properties to its element
		# So don't compute anything
		pass

	def get(self, name):
		if name in self.properties:
			return super().get(name)
		else:
			return self.animation.element.get(name)

	def set(self, name, value):
		if name in self.properties:
			super().set(name, value)
		else:
			element = self.animation.element
			# element.set(name, value)
			element.check_value(name, value)

			property = element.get(name)
			property.check_assignable(dynamic=True)

			property.keyframes.append(self)

			super().define(name, value, relative=property.relative)
			self.element_properties.append(name)

	def add(self, element):
		raise NotImplementedError

	@property
	def animation(self):
		return self.parent

	@property
	def time(self):
		return self.p_time

	def __lt__(self, other):
		return self.time < other.time

	def __repr__(self):
		return f"<{self.__class__.__name__}: {self.time}>"
