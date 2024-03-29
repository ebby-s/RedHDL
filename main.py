import argparse
from mcpi.connection import Connection
from mcpi.vec3 import Vec3

from file_handler import FileHandler
from world_parser import WorldParser, getAdjBlocks

# Parse optional CLI arguments.
parser = argparse.ArgumentParser(description='RedHDL CLI options')
parser.add_argument('--out', '-o', default='rs_out.sv', type=str,
                    help='Path to output file. (rs_out.sv)')
parser.add_argument('--width', '-w', default='40', type=int,
                    help='Horizontal radius of search area. (40)')
parser.add_argument('--height', '-r', default='20', type=int,
                    help='Height of search area. (20)')

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

def sameAxis(dir1, dir2):
    axis1 = ['north', 'south']
    axis2 = ['west', 'east']

    return ((dir1 in axis1) and (dir2 in axis1)) or ((dir1 in axis2) and (dir2 in axis2))

# Get CLI arguments.
args = parser.parse_args()

# Connect to the local Minecraft server.
conn = Connection("127.0.0.1", 4712)

# Create output file.
sv_out = FileHandler(args.out)

# Create parser.
parser = WorldParser(conn, args.width, args.height)
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

    ppt = parser.rs_ppts[item.x][item.y][item.z][1]

    sv_out.addDef('p0_'+vecToStr(item), '(i_'+vecToStr(item)+'<<2)')

    if ppt['face'] == 'CEILING':
        sv_out.addDef('p0_'+vecToStr(item+Vec3(0,1,0)), '(p0_'+vecToStr(item)+"&3'h4)")
    elif ppt['face'] == 'FLOOR':
        sv_out.addDef('p0_'+vecToStr(item+Vec3(0,-1,0)), '(p0_'+vecToStr(item)+"&3'h4)")
    else:
        sv_out.addDef('p0_'+vecToStr(item+dirToVec(ppt['facing'])), '(p0_'+vecToStr(item)+"&3'h4)")

# Add definitons for Redstone blocks, torches and repeaters.
for item in parser.rs_components:

    block_id = parser.rs_ppts[item.x][item.y][item.z][0]
    ppt = parser.rs_ppts[item.x][item.y][item.z][1]

    if block_id == 'REDSTONE_BLOCK':
        sv_out.addDef('p0_'+vecToStr(item), "3'h4")

    elif 'TORCH' in block_id:

        above = item+Vec3(0,1,0)
        if vecToTuple(above) in parser.rs_blocks:
            if (above not in parser.rs_inputs) and (above not in parser.rs_components):
                sv_out.addDef('p0_'+vecToStr(above), '(p0_'+vecToStr(item)+"&3'h4)")

        if 'WALL' in block_id:
            sv_out.addTorch(vecToStr(item), '(~|p0_'+vecToStr(item+dirToVec(ppt['facing']))+'[2:1])')
        else:
            sv_out.addTorch(vecToStr(item), '(~|p0_'+vecToStr(item+Vec3(0,-1,0))+'[2:1])')

    elif block_id == 'REPEATER':

        src_blk = item-dirToVec(ppt['facing'])
        dst_blk = item+dirToVec(ppt['facing'])

        if vecToTuple(dst_blk) not in parser.rs_blocks:
            continue
        if dst_blk in parser.rs_inputs:
            continue

        dst_id  = parser.rs_ppts[dst_blk.x][dst_blk.y][dst_blk.z][0]
        dst_ppt = parser.rs_ppts[dst_blk.x][dst_blk.y][dst_blk.z][1]
        src_id  = parser.rs_ppts[src_blk.x][src_blk.y][src_blk.z][0]
        src_ppt = parser.rs_ppts[src_blk.x][src_blk.y][src_blk.z][1]

        if vecToTuple(src_blk) not in parser.rs_blocks:
            line = '0'
        elif ('WIRE' in src_id) or (src_id == 'REPEATER'):
            line = 'rp_'+vecToStr(item)
        else:
            line = '(|p0_'+vecToStr(src_blk)+'[2:1])'

        if dst_blk not in parser.rs_components:
            sv_out.addFlop(vecToStr(dst_blk), line, int(ppt['delay']), vecToStr(item))
        elif 'WIRE' in dst_id:
            sv_out.addRep(vecToStr(dst_blk), line, int(ppt['delay']), vecToStr(item))
        elif dst_id == 'REPEATER':
            if ppt['facing'] == dst_ppt['facing']:
                sv_out.addRep(vecToStr(dst_blk), line, int(ppt['delay']), vecToStr(item))
            elif not sameAxis(ppt['facing'], dst_ppt['facing']):
                sv_out.addEnable(vecToStr(dst_blk), line, int(ppt['delay']), vecToStr(item))

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

    sides = [Vec3(1,0,0), Vec3(-1,0,0), Vec3(0,0,1), Vec3(0,0,-1), Vec3(0,1,0), Vec3(0,0,0), Vec3(0,-1,0)]

    sv_out.addDeclr('w_'+vecToStr(group[0]))

    for adj, wire, side in [(wire+side, wire, side) for side in sides for wire in group]:

        if vecToTuple(adj) in parser.rs_blocks:

            sv_out.addDef('w_'+vecToStr(group[0]), 'p0_'+vecToStr(adj)+'[2]')

            if side == Vec3(0,-1,0):
                sv_out.addDef('p0_'+vecToStr(adj), '(w_'+vecToStr(group[0])+'<<1)')
            elif side in [Vec3(1,0,0), Vec3(-1,0,0), Vec3(0,0,1), Vec3(0,0,-1)]:
                if (parser.rs_ppts[wire.x][wire.y][wire.z][1][vecToDir(-side)] == 'side') and (adj not in parser.rs_inputs):
                    if (adj not in parser.rs_components):
                        sv_out.addDef('p0_'+vecToStr(adj), '(w_'+vecToStr(group[0])+'<<1)')
                    elif parser.rs_ppts[adj.x][adj.y][adj.z][0] == 'REPEATER':
                        if parser.rs_ppts[adj.x][adj.y][adj.z][1]['facing'] == vecToDir(side):
                            sv_out.addRep(vecToStr(adj), 'w_'+vecToStr(group[0]))
                        elif parser.rs_ppts[adj.x][adj.y][adj.z][1]['facing'] == vecToDir(-side):
                            sv_out.addDef('w_'+vecToStr(group[0]), 'rp_'+vecToStr(wire))

# Assign power from charged blocks.
for item in parser.rs_outputs:
    for adj in getAdjBlocks(item):
        if vecToTuple(adj) in parser.rs_blocks:
            sv_out.addDef('p0_'+vecToStr(item), "{2'h0,|p0_"+vecToStr(adj)+'[2:1]}')


sv_out.writeFile()

