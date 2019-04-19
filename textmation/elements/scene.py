#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..datatypes import *
from .drawables import BaseDrawable


class Scene(BaseDrawable):
	def on_ready(self):
		super().on_ready()

		self.define("width", 100, Number)
		self.define("height", 100, Number)

		self.define("background", Vec4(0, 0, 0, 255))

		self.define("frame_rate", 20, Number)

		# TODO: Calculate total duration by default
		self.define("duration", 1, Number)

		# TODO: What should be default?
		self.define("inclusive", 1, Number)
