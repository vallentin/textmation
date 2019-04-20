#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import abspath, dirname, join
from argparse import ArgumentParser

from .parser import parse
from .scenebuilder import SceneBuilder
from .rasterizer import Image
from .renderer import render_animation, calc_frame_count
from .pretty import pprint_ast, pprint_element


if __name__ == "__main__":
	args_parser = ArgumentParser()
	args_parser.add_argument("-o", "--output", default="output.gif", help="Output filename")
	args_parser.add_argument("filename", help="Textmation file to process")
	args_parser.add_argument("--save-frames", action="store_const", const=True, default=False)
	args_parser.add_argument("--print-ast", action="store_const", const=True, default=False)
	args_parser.add_argument("--print-scene", action="store_const", const=True, default=False)

	args = args_parser.parse_args()

	output_dir = abspath(dirname(args.output))

	with open(args.filename) as f:
		string = f.read()

	print("Parsing...", flush=True)

	tree = parse(string)

	if args.print_ast:
		pprint_ast(tree)

	print("Building Scene...", flush=True)

	builder = SceneBuilder()
	scene = builder.build(tree)

	if args.print_scene:
		pprint_element(scene)

	print(f"Rendering {calc_frame_count(scene.p_duration.seconds, scene.p_frame_rate, inclusive=scene.p_inclusive)} frames...", flush=True)

	inclusive = bool(scene.p_inclusive)
	frames = render_animation(scene, inclusive=inclusive)

	if args.save_frames:
		print("Exporting Frames...", flush=True)

		frames_dir = join(output_dir, "frames")

		os.makedirs(frames_dir, exist_ok=True)

		for i, frame in enumerate(frames, start=1):
			frame.save(join(frames_dir, f"frame_{i:04d}.png"))

	print("Exporting Animation...", flush=True)

	os.makedirs(output_dir, exist_ok=True)

	Image.save_gif(args.output, frames, scene.p_frame_rate)
