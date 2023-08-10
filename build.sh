#!/bin/sh

# Add OSS tools to path.
export PATH=/home/ebby/oss-cad-suite/bin:$PATH

# Go to project directory.
cd orangecrab

echo "[INFO] Generating bitstream."

make clean >/dev/null
make all >/dev/null 2>/dev/null

echo "[INFO] Flashing to device."

make dfu
