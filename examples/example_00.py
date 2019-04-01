#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from textmation import *

from examples.example import timeit


class FadeInOut(Animation):
	def __init__(self, duration, delay=0.0):
		super().__init__("color.alpha")
		self.delay = delay
		self.add(Keyframe(0, 0))
		self.add(Keyframe(duration * 0.5, 105))
		self.add(Keyframe(duration, 0))


@timeit()
def example_01():
	scene = Scene(Size(200, 200), Color(0, 0, 0))

	r1 = Rectangle(Rect(Point(10, 10), Size(85, 85)), Color(255, 0, 0))
	r2 = Rectangle(Rect(Point(105, 10), Size(85, 85)), Color(0, 255, 0))
	r3 = Rectangle(Rect(Point(10, 105), Size(85, 85)), Color(0, 0, 255))
	r4 = Rectangle(Rect(Point(105, 105), Size(85, 85)), Color(255, 0, 255))
	scene.add_all((r1, r2, r3, r4))

	r1.add(FadeInOut(2))
	r2.add(FadeInOut(2, 0.5))
	r3.add(FadeInOut(2, 1.0))
	r4.add(FadeInOut(2, 1.5))

	frames = render_animation(scene, inclusive=True)

	os.makedirs("output", exist_ok=True)

	for i, frame in enumerate(frames, start=1):
		filename = "output/frame_%04d.png" % i
		frame.save(filename)

	Image.save_gif("output.gif", frames, scene.frame_rate)


if __name__ == "__main__":
	example_01()
