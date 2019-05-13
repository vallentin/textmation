#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import join, dirname, abspath
from importlib.util import spec_from_file_location, module_from_spec


_textmation_dir = abspath(join(dirname(__file__), os.pardir))

if os.name == "nt":
	_rasterizer_pyd = abspath(join(_textmation_dir, "rasterizer.pyd"))
else:
	_rasterizer_pyd = abspath(join(_textmation_dir, "rasterizer.so"))


spec = spec_from_file_location("rasterizer", _rasterizer_pyd)
rasterizer = module_from_spec(spec)
spec.loader.exec_module(rasterizer)

Image, Font = rasterizer.PyImage, rasterizer.PyFont


_images = {}
_fonts = {}


def load_image(filename):
	try:
		return _images[filename]
	except KeyError:
		image = Image.load(filename)
		_images[filename] = image
		return image


def load_font(font):
	try:
		return _fonts[font]
	except KeyError:
		_font = Font.load(font)
		_fonts[font] = _font
		return _font


def to_color(color):
	return tuple(max(min(r, 255), 0) for r in color)
