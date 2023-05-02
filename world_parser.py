import re

from mcpi.minecraft import intFloor
from mcpi.vec3 import Vec3


# Examples of responses to block data requests.
'''
EnumProperty{name=face, clazz=class net.minecraft.world.level.block.state.properties.AttachFace, values=[FLOOR, WALL, CEILING]}=WALL
EnumProperty{name=east, clazz=class net.minecraft.world.level.block.state.properties.RedstoneSide, values=[up, side, none]}=none
EnumProperty{name=north, clazz=class net.minecraft.world.level.block.state.properties.RedstoneSide, values=[up, side, none]}=side
EnumProperty{name=south, clazz=class net.minecraft.world.level.block.state.properties.RedstoneSide, values=[up, side, none]}=up
EnumProperty{name=west, clazz=class net.minecraft.world.level.block.state.properties.RedstoneSide, values=[up, side, none]}=side

DirectionProperty{name=facing, clazz=class net.minecraft.core.Direction, values=[north, south, west, east]}=east

BooleanProperty{name=powered, clazz=class java.lang.Boolean, values=[true, false]}=false
BooleanProperty{name=lit, clazz=class java.lang.Boolean, values=[true, false]}=false
BooleanProperty{name=locked, clazz=class java.lang.Boolean, values=[true, false]}=false


IntegerProperty{name=power, clazz=class java.lang.Integer, values=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]}=0
IntegerProperty{name=delay, clazz=class java.lang.Integer, values=[1, 2, 3, 4]}=1
'''


def getAdjBlocks(pos):
    out = []
    for dis in [Vec3(1,0,0), Vec3(0,1,0), Vec3(0,0,1)]:
        out += [pos-dis, pos+dis]
    return out

def parseData(data):
    names = [x.split("=")[1] for x in re.findall("name=[a-z]+", data)]
    values = re.findall("}=([a-z]+|[0-9]+|[A-Z]+)", data)
    return names, values


class WorldParser:

    def __init__(self, conn, search_range):
        self.conn = conn
        self.search_range = search_range
        # Store properties
        self.rs_ppts = [[[[] for k in range(40)] for j in range(40)] for i in range(40)]
        # Store all relevant blocks, remove duplicates
        self.rs_blocks = set()
        # Store locations of inputs, outputs and other components
        self.rs_inputs = []
        self.rs_components = []
        self.rs_outputs = []

    def getPlayerPos(self):
        s = self.conn.sendReceive(b"player" + b".getPos", [])
        return Vec3(*list(map(float, s.split(","))))

    def getBlockData(self, pos):
        return self.conn.sendReceive(b"world.getBlockWithData", intFloor(pos.x, pos.y, pos.z))

    def processBlock(self, pos,i,j,k, block_id, block_state_str):

        if any(x in block_id for x in ('REDSTONE', 'LEVER', 'BUTTON', 'REPEATER')):

            # Parse data into dict
            names, values = parseData(block_state_str)
            properties = dict(zip(names, values))

            # Store data in properties list
            self.rs_ppts[i][j][k] = [block_id, properties]

            # Add location to rs lists.
            if 'LAMP' in block_id:
                self.rs_outputs.append(Vec3(i,j,k))
            elif any(x in block_id for x in ('LEVER', 'BUTTON')):
                self.rs_inputs.append(Vec3(i,j,k))
            else:
                self.rs_components.append(Vec3(i,j,k))

            # Add relevant blocks to set
            self.rs_blocks.add((i,j,k))
            for block in getAdjBlocks(Vec3(i,j,k)):
                if self.getBlockData(pos+block).split(',')[0] != 'AIR':
                    self.rs_blocks.add((block.x, block.y, block.z))

    def captureWorldState(self):

        # Reset previous values
        self.rs_ppts = [[[[] for k in range(40)] for j in range(40)] for i in range(40)]
        self.rs_blocks = set()
        self.rs_inputs = []
        self.rs_components = []
        self.rs_outputs = []

        # Center search on player position
        pos = self.getPlayerPos()
        # Change pos to bottom-north-west corner of search area
        pos -= Vec3(self.search_range,self.search_range,self.search_range)

        # Search 3D area, record relevant blocks and properties
        for i in range(2*self.search_range):
            for j in range(2*self.search_range):
                for k in range(2*self.search_range):

                    # Get current block data.
                    data = self.getBlockData(pos+Vec3(i,j,k))

                    # Split data into block ID and state.
                    split_idx = data.index(',')
                    block_id = data[:split_idx]
                    block_state_str = data[split_idx+1:]

                    # If block is relevant to redstone, parse further.
                    self.processBlock(pos,i,j,k, block_id, block_state_str)






