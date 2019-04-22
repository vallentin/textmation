#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import ceil
import os
from os.path import abspath, dirname, join
import time
from argparse import ArgumentParser

from .parser import parse
from .scenebuilder import SceneBuilder
from .rasterizer import Image
from .renderer import render_animation, calc_frame_count
from .pretty import pretty_duration, pprint_ast, pprint_element


def run(input_filename, output_filename, *, save_frames=False, print_ast=False, print_scene=False):
	begin = time.time()

	output_dir = abspath(dirname(output_filename))

	with open(input_filename) as f:
		string = f.read()

	print("Parsing...", flush=True)

	tree = parse(string)

	if print_ast:
		pprint_ast(tree)

	print("Building Scene...", flush=True)

	builder = SceneBuilder()
	scene = builder.build(tree)

	if print_scene:
		pprint_element(scene)

	print(f"Rendering {calc_frame_count(scene.p_duration.seconds, scene.p_frame_rate, inclusive=scene.p_inclusive)} frames...", flush=True)

	inclusive = bool(scene.p_inclusive)
	frames = render_animation(scene, inclusive=inclusive)

	if save_frames:
		print("Exporting Frames...", flush=True)

		frames_dir = join(output_dir, "frames")

		os.makedirs(frames_dir, exist_ok=True)

		for i, frame in enumerate(frames, start=1):
			frame.save(join(frames_dir, f"frame_{i:04d}.png"))

	print("Exporting Animation...", flush=True)

	os.makedirs(output_dir, exist_ok=True)

	Image.save_gif(output_filename, frames, scene.p_frame_rate)

	end = time.time()
	duration = end - begin
	print(f"Rendered in {pretty_duration(ceil(duration))}")


def main():
	args_parser = ArgumentParser()
	args_parser.add_argument("-o", "--output", default="output.gif", help="Output filename")
	args_parser.add_argument("filename", help="Textmation file to process")
	args_parser.add_argument("--save-frames", action="store_const", const=True, default=False)
	args_parser.add_argument("--print-ast", action="store_const", const=True, default=False)
	args_parser.add_argument("--print-scene", action="store_const", const=True, default=False)

	args = args_parser.parse_args()

	run(args.filename, args.output, save_frames=args.save_frames, print_ast=args.print_ast, print_scene=args.print_scene)


if __name__ == "__main__":
	main()
