#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import exists, isfile, join, dirname, abspath, relpath
import re
from zipfile import ZipFile

from .elements import ElementError, Image
from .webtools import *


_textmation_dir = abspath(join(dirname(__file__), os.pardir))
_cache_dir = abspath(join(_textmation_dir, ".cache"))
_images_dir = join(_cache_dir, "images")
_fonts_dir = join(_textmation_dir, "fonts")


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


def _download_font(url):
	if url.endswith(".ttf"):
		font_name = re.search(r"\/([\w+\-\.]+)$", url)
		assert font_name is not None
		font_name = font_name.group(1)

		filename = join(_fonts_dir, font_name)

		print("Downloading:", url, "->", relpath(filename), flush=True)

		os.makedirs(_fonts_dir, exist_ok=True)
		download(url, filename)

		print("Downloaded:", url, "->", relpath(filename), flush=True)
	elif "fonts.google.com" in url:
		font_name = re.search(r"\/([\w+\-\.]+)$", url)
		assert font_name is not None
		font_name = font_name.group(1)

		font_name = font_name.replace("+", "%20")
		url = f"https://fonts.google.com/download?family={font_name}"

		filename = join(_fonts_dir, "font.zip")

		print("Downloading:", url, "->", relpath(filename), flush=True)

		os.makedirs(_fonts_dir, exist_ok=True)
		download(url, filename)

		print("Downloaded:", url, "->", relpath(filename), flush=True)
		print("Unpacking", relpath(filename), flush=True)

		with ZipFile(filename, "r") as zip:
			zip.extractall(_fonts_dir)

		print("Unpacked", relpath(filename), flush=True)
		print("Removing", relpath(filename), flush=True)

		os.remove(filename)
	else:
		raise Exception("Unsupported font service\nSupported: https://fonts.google.com")


def _download_fonts(scene):
	default_fonts = [
		(join(_fonts_dir, "Montserrat-Regular.ttf"), "https://fonts.google.com/specimen/Montserrat"),
		(join(_fonts_dir, "fa-brands-400.ttf"), "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.8.2/webfonts/fa-brands-400.ttf"),
	]

	for filename, url in default_fonts:
		if not exists(filename):
			_download_font(url)


def prepare(scene):
	_download_images(scene)
	_download_fonts(scene)
	return scene
