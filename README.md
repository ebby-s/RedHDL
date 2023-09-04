# RedHDL
Convert Redstone circuits from Minecraft into synthesizable System Verilog.

# Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Features](#features)
5. [Examples](#examples)
    *  [Basic Logic Gates](#logic_gates)
    *  [Adder](#adder)
    *  [Binary Counter](#counter)
6. [License](#license)

<a name="overview"></a>
# 1 Overview

[rj_og]: https://github.com/zhuowei/RaspberryJuice

[rj_fork]: https://github.com/wensheng/JuicyRaspberryPie

[mcpi_link]: https://github.com/martinohanlon/mcpi

This project aims to provide the ability to design digital logic in redstone, and convert to system verilog. The output could then be loaded onto an FPGA Dev Board or simulator. Another goal of this project is to make the source as simple and easy to understand as possible, which is why it is written in Python without using too many advanced features of the language.

Currently, this project is compatible with Minecraft Java 1.18.1, but requires the [RaspberryJuice][rj_og] mod (specifically [this][rj_fork] fork which supports 1.18.1) and the [mcpi][mcpi_link] library for Python.

<a name="installation"></a>
# 2 Installation

[forge_dl]: https://files.minecraftforge.net/net/minecraftforge/forge/index_1.18.1.html

[jrp_dl]: https://github.com/wensheng/JuicyRaspberryPie/releases/download/v0.3/juicyraspberrypie-forge-1.18.1.jar

In order to use this project, follow these steps:

1. Install [Forge 39.1.0][forge_dl] with Minecraft Java 1.18.1.

3. Download and install [JuicyRaspberryPie v0.3][jrp_dl].

4. Get the [mcpi][mcpi_link] Python library.

Now you're ready to go!


<a name="usage"></a>
# 3 Usage

## 3.1 Minecraft to System Verilog

Before running this program, you need to:

1. Have Minecraft open, with the target world loaded.

2. The player needs to be at the location of the taret redstone circuits because the program only scans a volume of blocks with the player at the centre.

When these conditions are met, go to a terminal and run the following command:
`python main.py -o rs_out.sv -w 40 -r 20`

The output will be generated and written to a file named `rs_out.sv`, in the same directory. The search area is 80x40x80.

## 3.2 Minecraft to OrangeCrab

Alternatively, the `orangecrab` directory contains all the files required to take the output SV file and program an OrangeCrab board (r0.2.1). The `run.bat` and `build.sh` scripts automate this process.


<a name="features"></a>
# 4 Features

Currently, both combinational and sequential circuits are supported with a single clock. In-game, the Redstone clock ticks at 10Hz, this Redstone clock is used as the reference clock for all sequential circuits. Additional clocks can be generated using dividers for now.

Fully implemented components:

- Redstone Lamp - This is the only component that generates an output in the RTL. It generates a 1-bit output signal.

- Lever/Button - These components are inputs to the system. They generate 1-bit input signals.

- Redstone Torch - An inverter followed by a delay of 1 cycle.

- Redstone Block - Constant '1' source.

- Repeater - A delay of 1-4 cycles, set at compile-time. The 'locking' mechanism from Redstone is available, it is added as an enable signal in the RTL.

- Redstone Wire - Behaviour of the RTL matches Redstone, but signals do not decay in thr RTL. This component can be used to perform the logical OR operation.

Future ideas:

- Use signs keywords such as `SOURCE`, `DESTINATION`, `INPUT` and `OUTPUT` to name signals within the world.

- Add another mode which allows full custom IC design. Components map to analogue rather than using System Verilog.



<a name="examples"></a>
# 5 Examples

There are examples available in the `example_worlds` directory. This directory contains minecraft worlds with redstone designs.

<a name="logic_gates"></a>
## 5.1 Logic Gates

A demonstration of the basic logic operations (AND, OR, XOR). These are built using the logical OR and NOT operations provided by Redstone wires & torches respectively.

<a name="adder"></a>
## 5.2 Adder

This example contains a 2-bit adder, made with full adders.

<a name="counter"></a>
## 5.3 Binary Counter

Using a 21-bit binary counter which ticks with the 48 MHz OrangeCrab clock, it is possible to slow the clock down enough to watch the high side bits count with human eyes. This example accomplishes exactly that.


<a name="license"></a>
# 6 License

This project is under the MIT License, see `LICENSE` for details.

