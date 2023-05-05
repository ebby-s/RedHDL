from mcpi.connection import Connection
from mcpi.vec3 import Vec3

from file_handler import FileHandler
from world_parser import WorldParser


def vecToStr(pos):
    return str(pos.x) + '_' + str(pos.y) + '_' + str(pos.z)


def dirToVec(facing):
    if(facing == 'north'):
        return Vec3(0,0,1)
    elif(facing == 'south'):
        return Vec3(0,0,-1)
    elif(facing == 'east'):
        return Vec3(-1,0,0)
    elif(facing == 'west'):
        return Vec3(1,0,0)



# Connect to the local Minecraft server.
conn = Connection("127.0.0.1", 4712)

# Create output file.
sv_out = FileHandler('rs_out.sv')

# Create parser.
parser = WorldParser(conn, 20)
# Parse current world.
parser.captureWorldState()



# Register inputs, outputs and relevant blocks with file handler.
for item in parser.rs_inputs:
    sv_out.addInput(vecToStr(item))

for item in parser.rs_outputs:
    sv_out.addOutput(vecToStr(item))

for item in parser.rs_blocks:
    sv_out.addDeclr(vecToStr(Vec3(*item)))

# Define signals related to inputs.
for item in parser.rs_inputs:

    sv_out.addDef(vecToStr(item), '(i_'+vecToStr(item)+'<<2)')

    ppt = parser.rs_ppts[item.x][item.y][item.z][1]

    if ppt['face'] == 'CEILING':
        sv_out.addDef(vecToStr(item+Vec3(0,1,0)), '(p0_'+vecToStr(item)+"&3'h4)")
    elif ppt['face'] == 'FLOOR':
        sv_out.addDef(vecToStr(item+Vec3(0,-1,0)), '(p0_'+vecToStr(item)+"&3'h4)")
    else:
        sv_out.addDef(vecToStr(item+dirToVec(ppt['facing'])), '(p0_'+vecToStr(item)+"&3'h4)")

# Add definitons for Redstone blocks, torches and repeaters.
for item in parser.rs_components:

    block_id = parser.rs_ppts[item.x][item.y][item.z][0]
    ppt = parser.rs_ppts[item.x][item.y][item.z][1]

    if block_id == 'REDSTONE_BLOCK':
        sv_out.addDef(vecToStr(item), "3'h4")

    elif 'TORCH' in block_id:

        above = item+Vec3(0,1,0)

        if (above.x,above.y,above.z) in parser.rs_blocks:
            if (above not in parser.rs_inputs) and (above not in parser.rs_components):
                sv_out.addDef(vecToStr(above), '(p0_'+vecToStr(item)+"&3'h4)")

        if 'WALL' in block_id:
            sv_out.addDef(vecToStr(item), '((~p0_'+vecToStr(item+dirToVec(ppt['facing']))+")&3'h4)")
        else:
            sv_out.addDef(vecToStr(item), '((~p0_'+vecToStr(item+Vec3(0,-1,0))+")&3'h4)")

    elif block_id == 'REPEATER':

        src_blk = item-dirToVec(ppt['facing'])
        dst_blk = item+dirToVec(ppt['facing'])

        if (dst_blk not in parser.rs_inputs) and (dst_blk not in parser.rs_components):
            sv_out.addDef(vecToStr(dst_blk), '((|p0_'+vecToStr(src_blk)+"[2:1])<<2)")


# Make wires and connect to blocks.


# Assign power from charged blocks.





sv_out.writeFile()

