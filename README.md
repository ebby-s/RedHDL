# RedHDL
Convert Redstone circuits from Minecraft into synthesizable System Verilog.

# Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Features](#features)
5. [Examples](#examples)
    *  [Basic Logic Gates](#overview)
    *  [Adder circuit](#overview)
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

Before running this program, you need to:

1. Have Minecraft open, with the target world loaded.

2. The player needs to be at the location of the taret redstone circuits because the program only scans a 40x40x40 area with the player in the centre.

When these conditions are met, go to a terminal and run `main.py`.

The output will be generated and written to a file named `rs_out.sv`, in the same directory.



<a name="features"></a>
# 4 Features

Currently, only combinatorial circuits are supported. Support for components such as latches and flip-flops could be added in the future, but will change the mapping from redstone to HDL significantly.

Components fully implemented:

- Redstone Lamp - This is the only component that generates an output in HDL. It generates a 1-bit output signal.

- Lever/Button - These components are inputs to the system. They generate 1-bit input signals.

- Redstone Torch - As in redstone, this can be used as an inverter.

- Redstone Block - Constantly powered.

The next set of components could change behaviour depending on whether latches and flip-flops are supported.

In progress:

- Repeater - Depending on the mode, acts as a buffer, latch or flip-flop.

- Redstone Wire

In the future, maybe signs could be used to name signals, and declare them as inputs or outputs.

Future ideas:

- Signs - Use keywords such as `SOURCE`, `DESTINATION`, `INPUT` and `OUTPUT` to name signals within the world.



<a name="Examples"></a>
# 5 Examples

TODO

<a name="license"></a>
# 6 License

This project is under the MIT License, see `LICENSE` for details.

