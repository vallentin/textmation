#!/usr/bin/env python
# -*- coding: utf-8 -*-


def fold_constants(scene):
	for element in scene.traverse():
		for property in element.properties.values():
			if property.readonly:
				continue
			property.set(property.get().fold())
	return scene
