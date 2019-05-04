#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from math import ceil
import os
from os.path import abspath, dirname, join
import time
import subprocess
from argparse import ArgumentParser

from .parser import parse
from .scenebuilder import SceneBuilder
from .optimizations import optimize
from .rasterizer import Image
from .renderer import render_animation, calc_frame_count
from .pretty import pretty_duration, pprint_ast, pprint_element


_ffmpeg_formats = ".mp4", ".avi", ".webm"
_formats = ".gif", *_ffmpeg_formats


def run(input_filename, output_filename, *, save_frames=False, print_ast=False, print_scene=False):
	begin = time.time()

	output_dir = abspath(dirname(output_filename))
	frames_dir = join(output_dir, "frames")
	frames_basename_format = "frame_%04d.png"

	needs_ffmpeg = output_filename.lower().endswith(_ffmpeg_formats)
	save_frames = save_frames or needs_ffmpeg

	if not output_filename.lower().endswith(_formats):
		ext = os.path.splitext(output_filename)[1]
		print(f"Unknown export format {ext}, expected any of", ", ".join(_formats), file=sys.stderr)
		exit(1)

	print(f"Processing: {os.path.relpath(input_filename)}")

	with open(input_filename) as f:
		string = f.read()

	print("Parsing...", flush=True)

	tree = parse(string)

	if print_ast:
		pprint_ast(tree)

	print("Building Scene...", flush=True)

	builder = SceneBuilder()
	scene = builder.build(tree)

	print("Optimizing Scene...", flush=True)

	scene = optimize(scene)

	if print_scene:
		pprint_element(scene)

	print(f"Rendering {calc_frame_count(scene.p_duration.seconds, scene.p_frame_rate, inclusive=scene.p_inclusive)} frames...", flush=True)

	inclusive = bool(scene.p_inclusive)
	frames = render_animation(scene, inclusive=inclusive)

	if save_frames:
		print("Exporting Frames...", flush=True)

		os.makedirs(frames_dir, exist_ok=True)

		for i, frame in enumerate(frames, start=1):
			frame.save(join(frames_dir, frames_basename_format % i))

	print("Exporting Animation...", flush=True)

	os.makedirs(output_dir, exist_ok=True)

	if needs_ffmpeg:
		subprocess.run([
			"ffmpeg",
			"-y", "-loglevel", "error",
			"-framerate", str(scene.p_frame_rate),
			"-i", join(frames_dir, frames_basename_format),
			"-frames", str(len(frames)),
			output_filename,
		])
	else:
		Image.save_gif(output_filename, frames, scene.p_frame_rate)

	end = time.time()
	duration = end - begin
	print(f"Rendered in {pretty_duration(ceil(duration))}")


def try_run(input_filename, output_filename, *, save_frames=False, verbose=False, print_ast=False, print_scene=False):
	try:
		run(input_filename, output_filename, save_frames=save_frames, print_ast=print_ast, print_scene=print_scene)
		return 0
	except Exception as ex:
		sys.stdout.flush()
		time.sleep(0.1)

		if verbose or "PYCHARM_HOSTED" in os.environ:
			import traceback
			print(traceback.format_exc(), file=sys.stderr)
		else:
			print(f"{type(ex).__name__}: {ex}", file=sys.stderr)

		# TODO: Add more error codes based on the type of exception
		return 1


def main():
	args_parser = ArgumentParser()
	args_parser.add_argument("-o", "--output", default="output.gif", help="Output filename")
	args_parser.add_argument("filename", help="Textmation file to process")
	args_parser.add_argument("--save-frames", action="store_const", const=True, default=False)
	args_parser.add_argument("--print-ast", action="store_const", const=True, default=False)
	args_parser.add_argument("--print-scene", action="store_const", const=True, default=False)
	args_parser.add_argument("--verbose", action="store_const", const=True, default=False)

	args = args_parser.parse_args()

	return try_run(args.filename, args.output, save_frames=args.save_frames, verbose=args.verbose, print_ast=args.print_ast, print_scene=args.print_scene)


if __name__ == "__main__":
	exit(main())
