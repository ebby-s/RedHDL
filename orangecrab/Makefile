PROJ=red

VERSION:=r0.2.1


all: ${PROJ}.dfu

dfu: ${PROJ}.dfu
	dfu-util -a 0 -D $<


%.json: %.sv
	yosys -p "read_verilog -sv $< ${PROJ}_top.sv; synth_ecp5 -json $@"

%_out.config: %.json
	nextpnr-ecp5 --json $< --textcfg $@ --85k --package CSFBGA285 --lpf orangecrab_${VERSION}.pcf

%.bit: %_out.config
	ecppack --compress --freq 38.8 --input $< --bit $@

%.dfu : %.bit
	cp -a $< $@
	dfu-suffix -v 1209 -p 5af0 -a $@

clean:
	rm -rf ${PROJ}.bit ${PROJ}_out.config ${PROJ}.json ${PROJ}.dfu

.PHONY: prog clean
