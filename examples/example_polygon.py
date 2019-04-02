#!/usr/bin/env python
# -*- coding: utf-8 -*-

from textmation import *


def example_rasterizer():
	img = Image.new(Size(400, 400), Color(0, 0, 0))

	points_first = (Point(20,20), Point(20,150), Point(200,150))
	points_second = (Point(20,200), Point(20,350), Point(100,270), Point(230, 300))
	points_third = (Point(200,20), Point(180,30), Point(180,50), Point(200, 60), Point(220,50), Point(220,30))

	img.draw_polygon(points_first, Color(0, 0, 0), Color(0,0,255),3)
	img.draw_polygon(points_second, Color(255, 0, 0), Color(0,0,0),5)
	img.draw_polygon(points_third, Color(255, 255, 0), Color(120,230,0),2)



	img.save("output.png")


if __name__ == "__main__":
	example_rasterizer()

