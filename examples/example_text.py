#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import product

from textmation import *


def example_rasterizer():
	text = "Hello World\nFoo Bar\nTest"

	margin = 75
	spacing = 100

	combinations = list(product(Alignment, (Anchor.Left, Anchor.CenterX, Anchor.Right), (Anchor.Top, Anchor.CenterY, Anchor.Bottom)))

	n = len(combinations)
	columns = 9

	columns = min(columns, n)
	rows = ceil(n / columns)

	font = Font.load("arial", 13)

	text_width, text_height = font.measure_text(text)

	img_width  = margin * 2 + text_width * columns + spacing * (columns - 1)
	img_height = margin * 2 + text_height * rows + spacing * (rows - 1)

	img = Image.new(Size(img_width, img_height), Color(0, 0, 0))

	for i, (alignment, horizontal_anchor, vertical_anchor) in enumerate(combinations):
		anchor = horizontal_anchor | vertical_anchor

		print(i, alignment, anchor)

		ix, iy = i % columns, i // columns

		x = margin + (text_width + spacing) * ix
		y = margin + (text_height + spacing) * iy

		img.draw_rect(Rect(Point(x, y), Size(text_width, text_height)), Color(alpha=0), Color(255, 0, 0))
		img.draw_circle(Point(x, y), 4, Color(255, 255, 0))

		img.draw_text(text, Point(x, y), Color(255, 255, 255), font, anchor, alignment)

	img.save("output.png")


if __name__ == "__main__":
	example_rasterizer()
