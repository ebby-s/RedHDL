# Orangecrab Example

## Overview
The files in this directory can be used to build and run a generated design on an OrangeCrab r0.2.1.

## Files

- `red.v` — The top level module, declares input and output pins of the OrangeCrab FPGA, and maps them to the ports generated in redstone. This uses the `../rs_out.sv` file as the module definition generated from redstone.
- `Makefile` — The make build script that will produce the bitstream from the HDL. It makes uses of the open source tools `yosys`, `nextpnr`, `ecppack`, and `dfu-util` to go from hardware description to bitstream to running on the FPGA.

## Credits

[oc_eg]: https://github.com/orangecrab-fpga/orangecrab-examples

This is based on the examples found within the [OrangeCrab Examples][oc_eg] repository.
