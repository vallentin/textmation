#!/usr/bin/env bash

dirname=$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd -P)
cd "$dirname"

if [[ $@ == *"release"* ]]; then
	cargo build --release
else
	cargo build
fi

exit_code=$?
if [ $exit_code != 0 ]; then
	exit $exit_code
fi

rm -f rasterizer.pyd

if [[ $@ == *"release"* ]]; then
	cp target/release/rasterizer.dll rasterizer.pyd
else
	cp target/debug/rasterizer.dll rasterizer.pyd
fi
