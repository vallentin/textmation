#!/usr/bin/env python
# -*- coding: utf-8 -*-

from textmation import *

from examples.example import render_example, timeit


@timeit()
def example():
	margin = 10
	spacing = 5
	rect_width, rect_height = 10, 10

	scene_width  = 200
	scene_height = margin * 2 + rect_height * 5 + spacing * 4

	scene = Scene(Size(scene_width, scene_height), Color(20, 21, 24))

	r1 = Rectangle(Rect(Point(margin, margin + (rect_height + spacing) * 0), Size(rect_width, rect_height)), Color(38, 139, 210))
	r2 = Rectangle(Rect(Point(margin, margin + (rect_height + spacing) * 1), Size(rect_width, rect_height)), Color(38, 139, 210))
	r3 = Rectangle(Rect(Point(margin, margin + (rect_height + spacing) * 2), Size(rect_width, rect_height)), Color(38, 139, 210))
	r4 = Rectangle(Rect(Point(margin, margin + (rect_height + spacing) * 3), Size(rect_width, rect_height)), Color(38, 139, 210))
	r5 = Rectangle(Rect(Point(margin, margin + (rect_height + spacing) * 4), Size(rect_width, rect_height)), Color(38, 139, 210))

	scene.add_all((r1, r2, r3, r4, r5))

	r1a1 = Animation("width")
	r1a1.add(Keyframe(0, 0))
	r1a1.add(Keyframe(6, scene_width - rect_width - margin * 2))
	r1.add(r1a1)

	for r in (r2, r3, r4, r5):
		r2a1 = Animation("width")
		r2a1.delay = 1
		r2a1.fill_mode = AnimationFillMode.After
		r2a1.add(Keyframe(0, 0))
		r2a1.add(Keyframe(3, scene_width - rect_width - margin * 2))
		r.add(r2a1)

	r2a2 = Animation("color.red")
	r2a2.delay = r2a1.delay
	r2a2.fill_mode = AnimationFillMode.Never
	r2a2.add(Keyframe(0, 255))
	r2a2.add(Keyframe(r2a1.duration, 255))
	r2.add(r2a2)

	r3a2 = Animation("color.red")
	r3a2.delay = r2a1.delay
	r3a2.fill_mode = AnimationFillMode.After
	r3a2.add(Keyframe(0, 255))
	r3a2.add(Keyframe(r2a1.duration, 255))
	r3.add(r3a2)

	r4a2 = Animation("color.red")
	r4a2.delay = r2a1.delay
	r4a2.fill_mode = AnimationFillMode.Before
	r4a2.add(Keyframe(0, 255))
	r4a2.add(Keyframe(r2a1.duration, 255))
	r4.add(r4a2)

	r5a2 = Animation("color.red")
	r5a2.delay = r2a1.delay
	r5a2.fill_mode = AnimationFillMode.Always
	r5a2.add(Keyframe(0, 255))
	r5a2.add(Keyframe(r2a1.duration, 255))
	r5.add(r5a2)

	scene.frame_rate = 20

	render_example(scene)


if __name__ == "__main__":
	example()
