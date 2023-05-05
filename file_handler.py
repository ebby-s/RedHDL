from mcpi.vec3 import Vec3

class FileHandler:

    def __init__(self, name):

        self.name = name

        self.inputs = []
        self.outputs = []
        self.internal = []

        self.defs = {}

    def addInput(self, pos_string):
        self.inputs.append('i_' + pos_string)

    def addOutput(self, pos_string):
        self.outputs.append('o_' + pos_string)

    def addDeclr(self, pos_string):
        self.internal.append('p0_' + pos_string)
        self.defs['p0_' + pos_string] = []

    def addDef(self, pos_string, line):
        self.defs['p0_' + pos_string].append(line)

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
        handle.write('\t// Declare internal signals.\n')
        for line in self.internal:
            handle.write('\tlogic [2:0] ' + line + ';\n')

        handle.write('\n')

        # Assign internal signals
        handle.write('\t// Assign internal signals.\n')
        for line in self.defs:
            handle.write('\tassign ' + line + ' = ')

            if len(self.defs[line]) == 0:                # Set to zero if not defined.
                handle.write("0")
            for i, term in enumerate(self.defs[line]):
                if i != 0: handle.write(' | ')
                handle.write(term)
            handle.write(';\n')

        handle.write('\n')

        # Assign outputs
        handle.write('\t// Assign output signals.\n')
        for line in self.outputs:
            handle.write('\tassign ' + line + ' = |p0' + line[1:] + ';\n')


        handle.write('\nendmodule\n')  # End module definition

        handle.close()  # Write to output file and close

