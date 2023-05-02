from mcpi.vec3 import Vec3

class FileHandler:

    def __init__(self, name):

        self.name = name

        self.inputs = []
        self.outputs = []
        self.internal = []

        self.defs = []

    def addInput(self, pos):
        pos_string = str(pos.x) + '_' + str(pos.y) + '_' + str(pos.z)
        self.inputs.append('i_' + pos_string)

    def addOutput(self, pos):
        pos_string = str(pos.x) + '_' + str(pos.y) + '_' + str(pos.z)
        self.outputs.append('o_' + pos_string)

    def addDeclr(self, pos):
        pos_string = str(pos.x) + '_' + str(pos.y) + '_' + str(pos.z)

        declr_string = 'p0_' + pos_string

        if declr_string not in self.internal:
            self.internal.append(declr_string)

    def writeFile(self):

        # Create the output file.
        handle = open(self.name,'w')

        # Write header
        handle.write('module '+self.name.split('.')[0]+' (\n')

        # Declare inputs
        handle.write('\t// Declare input signals.\n')

        for line in self.inputs:
            handle.write('\tinput  logic ' + line + ';\n')

        # Declare outputs
        handle.write('\t// Declare output signals.\n')

        for line in self.outputs:
            handle.write('\toutput logic ' + line + ';\n')

        # Close header
        handle.write(');\n\n')

        # Declare internal signals
        handle.write('// Declare internal signals.\n')
        for line in self.internal:
            handle.write('\tlogic ' + line + ';\n')

        # Add definitions for internal signals
        for line in self.defs:  # define signals
            handle.write('\t' + line + ';\n')


        handle.write('\nendmodule\n')  # End module definition

        handle.close()  # Write to output file and close




