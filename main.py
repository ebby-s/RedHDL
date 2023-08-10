from mcpi.connection import Connection
from mcpi.vec3 import Vec3

from file_handler import FileHandler
from world_parser import WorldParser, getAdjBlocks

# Convert a Vec3 object to a string: x_y_z.
def vecToStr(pos):
    return str(pos.x) + '_' + str(pos.y) + '_' + str(pos.z)

# Convert cardinal direction to vector, and invert.
def dirToVec(facing):
    if(facing == 'north'):
        return Vec3(0,0,1)
    elif(facing == 'south'):
        return Vec3(0,0,-1)
    elif(facing == 'east'):
        return Vec3(-1,0,0)
    elif(facing == 'west'):
        return Vec3(1,0,0)

def vecToDir(vec):
    if(vec == Vec3(0,0,1)):
        return 'north'
    elif(vec == Vec3(0,0,-1)):
        return 'south'
    elif(vec == Vec3(-1,0,0)):
        return 'east'
    elif(vec == Vec3(1,0,0)):
        return 'west'

def vecToTuple(vec):
    return (vec.x, vec.y, vec.z)

def tupleToVec(tup):
    return Vec3(tup[0],tup[1],tup[2])



# Connect to the local Minecraft server.
conn = Connection("127.0.0.1", 4712)

# Create output file.
sv_out = FileHandler('orangecrab/red.sv')

# Create parser.
parser = WorldParser(conn, 20)
# Parse current world.
parser.captureWorldState()

rs_wires = []

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
            sv_out.addDef(vecToStr(item), '((~|p0_'+vecToStr(item+dirToVec(ppt['facing']))+"[2:1])<<2)")
        else:
            sv_out.addDef(vecToStr(item), '((~|p0_'+vecToStr(item+Vec3(0,-1,0))+"[2:1])<<2)")

    elif block_id == 'REPEATER':

        src_blk = item-dirToVec(ppt['facing'])
        dst_blk = item+dirToVec(ppt['facing'])

        if ((src_blk.x,src_blk.y,src_blk.z) not in parser.rs_blocks) or ((dst_blk.x,dst_blk.y,dst_blk.z) not in parser.rs_blocks):
            continue

        # Handle blocks.
        if (dst_blk not in parser.rs_inputs) and (dst_blk not in parser.rs_components):
            sv_out.addDef(vecToStr(dst_blk), '((|p0_'+vecToStr(src_blk)+"[2:1])<<2)")

        if dst_blk in parser.rs_components:
            # Handle wires.
            if 'WIRE' in parser.rs_ppts[dst_blk.x][dst_blk.y][dst_blk.z][0]:
                sv_out.addDef(vecToStr(dst_blk), '((|p0_'+vecToStr(src_blk)+"[2:1])<<2)")

            # Handle repeaters.
            if 'REPEATER' in parser.rs_ppts[dst_blk.x][dst_blk.y][dst_blk.z][0]:
                sv_out.addLatch(vecToStr(dst_blk+dirToVec(parser.rs_ppts[dst_blk.x][dst_blk.y][dst_blk.z][1]['facing'])), '(~|p0_'+vecToStr(src_blk)+"[2:1])")

    elif 'WIRE' in block_id:

        rs_wires.append(item)

# Find all neighbors of a redstone wire block.
def neighbors(graph, node, ppts):
    neighbors = []
    ppt = ppts[node.x][node.y][node.z][1]

    for key in ['north', 'south', 'east', 'west']:

        if ppt[key] == 'up':
            if (node - dirToVec(key) + Vec3(0,1,0)) in graph:
                neighbors.append((node - dirToVec(key) + Vec3(0,1,0)))
        if ppt[key] == 'side':
            if (node - dirToVec(key)) in graph:
                neighbors.append((node - dirToVec(key)))
            elif (node - dirToVec(key) + Vec3(0,-1,0)) in graph:
                neighbors.append((node - dirToVec(key) + Vec3(0,-1,0)))

    return neighbors

# Search (depth-first search) all wires connected to a node and group connected ones.
def dfs(graph, node, visited):

    visited.add(vecToTuple(node))
    group = [node]

    for neighbor in neighbors(graph, node, parser.rs_ppts):
        if vecToTuple(neighbor) not in visited:
            group_ext, visited = dfs(graph, neighbor, visited)
            group += group_ext

    return group, visited

# Group redstone wires
rs_wire_groups = []
visited = set()

for block in rs_wires:
    if vecToTuple(block) not in visited:
        group, visited = dfs(rs_wires, block, visited)
        rs_wire_groups.append(group)

# Connect wires to blocks.
for group in rs_wire_groups:

    sv_out.addDeclr(vecToStr(group[0]) + "_w")

    for wire in group:
        for side in [Vec3(0,-1,0)]:
            adj = wire + side
            if (adj.x,adj.y,adj.z) in parser.rs_blocks:
                sv_out.addDef(vecToStr(group[0]) + "_w", "p0_" + vecToStr(adj) + "[2]")
                sv_out.addDef(vecToStr(adj), "(p0_" + vecToStr(group[0]) + "_w << 1)")

        for side in [Vec3(0,1,0), Vec3(0,0,0)]:
            adj = wire + side
            if (adj.x,adj.y,adj.z) in parser.rs_blocks:
                sv_out.addDef(vecToStr(group[0]) + "_w", "p0_" + vecToStr(adj) + "[2]")

        for side in [Vec3(1,0,0), Vec3(-1,0,0), Vec3(0,0,1), Vec3(0,0,-1)]:
            adj = wire + side
            if (adj.x,adj.y,adj.z) in parser.rs_blocks:
                sv_out.addDef(vecToStr(group[0]) + "_w", "p0_" + vecToStr(adj) + "[2]")
                if(parser.rs_ppts[wire.x][wire.y][wire.z][1][vecToDir(-side)] == "side"):
                    sv_out.addDef(vecToStr(adj), "(p0_" + vecToStr(group[0]) + "_w << 1)")


# Assign power from charged blocks.
for item in parser.rs_outputs:
    for adj in getAdjBlocks(item):
        if(adj.x,adj.y,adj.z) in parser.rs_blocks:
            sv_out.addDef(vecToStr(item), "{2'h0,|p0_"+vecToStr(adj)+"[2:1]}")




sv_out.writeFile()

