#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import exists, isfile, join, dirname, abspath, relpath

from .elements import ElementError, Image
from .webtools import *


_cache_dir = abspath(join(dirname(__file__), os.pardir, ".cache"))
_images_dir = join(_cache_dir, "images")


def _download_image(url):
	filename = join(_images_dir, url2basename(url))

	if exists(filename):
		assert isfile(filename)
		return filename

	print("Downloading:", url, "->", relpath(filename), flush=True)

	os.makedirs(dirname(filename), exist_ok=True)
	download(url, filename)

	print("Downloaded:", url, "->", relpath(filename), flush=True)

	return filename


def _download_images(scene):
	for element in scene.traverse():
		if isinstance(element, Image):
			url = element.p_url
			filename = element.p_filename

			if not url:
				continue

			if not is_url(url):
				raise ElementError(f"Expected a URL, received {url!r}")

			if url and filename:
				# TODO: This doesn't include where
				raise ElementError("Both URL and filename specified")

			element.set("filename", _download_image(url))


def prepare(scene):
	_download_images(scene)
	return scene
