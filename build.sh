#!/bin/sh

export PATH=/home/ebby/oss-cad-suite/bin:$PATH

cd /mnt/c/Users/ebbys/Desktop/RedHDL/orangecrab

echo "[INFO] Generating bitstream."

make clean >/dev/null
make all >/dev/null 2>/dev/null

echo "[INFO] Flashing to device."

make dfu
