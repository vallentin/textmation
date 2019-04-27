#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .constantfolding import *


def optimize(scene):
	return fold_constants(scene)
