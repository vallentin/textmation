#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
from urllib.parse import urlparse
from urllib.request import urlretrieve


_valid_chars = frozenset("-_.%s%s" % (string.ascii_letters, string.digits))


def is_url(url):
	return urlparse(url).scheme.lower() in ("http", "https")


def url2basename(url):
	url = urlparse(url)
	url = f"{url.netloc}-{url.path}"
	return "".join(c for c in url if c in _valid_chars)


def download(url, filename):
	urlretrieve(url, filename)
