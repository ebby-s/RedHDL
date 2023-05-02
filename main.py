from mcpi.connection import Connection
from mcpi.vec3 import Vec3

from file_handler import FileHandler
from world_parser import WorldParser




conn = Connection("127.0.0.1", 4712)

sv_out = FileHandler('rs_out.sv')

parser = WorldParser(conn, 20)

parser.captureWorldState()




for item in parser.rs_inputs:
    sv_out.addInput(item)

for item in parser.rs_outputs:
    sv_out.addOutput(item)

for item in parser.rs_blocks:
    sv_out.addDeclr(Vec3(*item))





sv_out.writeFile()










