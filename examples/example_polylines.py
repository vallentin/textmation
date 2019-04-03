from textmation import *


def example_rasterizer():
	img = Image.new(Size(400, 400), Color(0, 0, 0))

	points_first = (Point(200, 20), Point(200, 150), Point(20, 150))
	points_second = (Point(20, 200), Point(20, 350), Point(100, 270), Point(230, 300))
	points_third = (Point(320, 200), Point(320, 350), Point(300, 270))
	points_fourth = (Point(320, 20), Point(320, 150), Point(350, 150), Point(370, 130))

	img.draw_polylines(points_first, Color(0, 0, 255), 3, join=Join.Round, cap=Cap.Butt)
	img.draw_polylines(points_second, Color(0, 0, 255), 8, join=Join.Miter, cap=Cap.Square)
	img.draw_polylines(points_third, Color(0, 0, 255), 5, join=Join.Round, cap=Cap.Round)
	img.draw_polylines(points_fourth, Color(0, 0, 255), 4, join=Join.Miter, cap=Cap.Square)

	img.save("output.png")


if __name__ == "__main__":
	example_rasterizer()

