#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import islice
from functools import total_ordering

from ..datatypes import Time, TimeUnit
from .element import Element, ElementError


def normalize(value, lower, upper):
	return (value - lower) / (upper - lower)


def lerp(a, b, t):
	# return a + t * (b - a) # Imprecise
	return (1 - t) * a + t * b # Precise


def remap(value, lower1, upper1, lower2, upper2):
	# return lower2 + (upper2 - lower2) * ((value - lower1) / (upper1 - lower1))
	return lerp(lower2, upper2, normalize(value, lower1, upper1))


class Animation(Element):
	def __init__(self):
		super().__init__()
		self.element_properties = None
		self.keyframes = []
		self._duration = Time(0, TimeUnit.Seconds)

	def on_ready(self):
		super().on_ready()

		self.define("duration", self._duration)

		self.define("delay", Time(0, TimeUnit.Seconds))

	def on_created(self):
		super().on_created()

		self.keyframes.sort()

		if len(self.keyframes) < 1:
			raise ElementError(f"{self.__class__.__name__} requires at least one keyframe")

		# Only calculate duration if it wasn't manually set
		if self._duration is self.get("duration").get():
			self.set("duration", max(self.keyframes).p_time)

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

		time = time - self.p_delay.seconds

		before, after = self.get_between(time)

		if before == after:
			for name in self.element_properties:
				self.element.set(name, before.eval(name))
		else:
			time = normalize(time, before.time.seconds, after.time.seconds)

			for name in self.element_properties:
				before_value = before.eval(name)
				after_value = after.eval(name)
				self.element.set(name, lerp(before_value, after_value, time))

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
		return self.p_duration

	@property
	def begin_time(self):
		return self.keyframes[0].time + self.p_delay

	@property
	def end_time(self):
		return self.begin_time + self.duration

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


@total_ordering
class Keyframe(Element):
	def __init__(self):
		super().__init__()
		self.element_properties = []

	def on_ready(self):
		super().on_ready()

		self.define("time", Time(0, TimeUnit.Seconds))

	def compute(self, time):
		# Keyframe is transparently setting properties to its element
		# So don't compute anything
		pass

	def set(self, name, value):
		if name in self.properties:
			super().set(name, value)
		else:
			element = self.animation.element
			# element.set(name, value)
			element.check_value(name, value)
			super().define(name, value, relative=element.get(name).relative)
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
