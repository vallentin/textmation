#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..datatypes import Number, Time, TimeUnit, Vec4
from .drawables import BaseDrawable
from .animation import Animation


def _duration(scene):
	duration = 0

	for element in scene.traverse():
		if isinstance(element, Animation):
			duration = max(duration, element.end_time)

	return Time(duration, TimeUnit.Seconds)


class Scene(BaseDrawable):
	def __init__(self):
		super().__init__()
		self._duration = Time(0, TimeUnit.Seconds)

	def on_ready(self):
		super().on_ready()

		self.define("width", 100, Number, constant=True)
		self.define("height", 100, Number, constant=True)

		self.define("background", Vec4(0, 0, 0, 255))

		self.define("frame_rate", 20, Number, constant=True)

		self.define("duration", self._duration, constant=True)

		self.define("inclusive", 1, Number, constant=True)

	def on_created(self):
		# Only calculate duration if it wasn't manually set
		if self._duration is self.get("duration").get():
			self.set("duration", _duration(self))
