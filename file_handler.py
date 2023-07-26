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
        self.defs['p0_' + pos_string] = set()

    def addDef(self, pos_string, line):
        self.defs['p0_' + pos_string].add(line)

    def writeFile(self):

        # Create the output file.
        handle = open(self.name,'w')

        # Write header
        handle.write('module '+self.name.split('.')[0].split('/')[-1]+' (\n')

        # Declare inputs
        handle.write('\t// Declare input signals.\n')

        for line in self.inputs[:-1]:
            handle.write('\tinput  logic ' + line + ',\n')
        if len(self.outputs) != 0:
            if len(self.inputs) != 0: handle.write('\tinput  logic ' + self.inputs[-1] + ',\n')
        else:
            if len(self.inputs) != 0: handle.write('\tinput  logic ' + self.inputs[-1] + '\n')

        # Declare outputs
        handle.write('\t// Declare output signals.\n')

        for line in self.outputs[:-1]:
            handle.write('\toutput logic ' + line + ',\n')
        if len(self.outputs) != 0: handle.write('\toutput logic ' + self.outputs[-1] + '\n')

        # Close header
        handle.write(');\n\n')

        # Declare internal signals
        handle.write('\t// Declare internal signals.\n')
        for line in self.internal:
            if line[-1] == 'w':
                handle.write('\tlogic       ' + line + ';\n')
            else:
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

        self.writeInstFile()


    def writeInstFile(self):

        # Read names of inputs and outputs.
        inputs = []
        outputs = []

        namefile = open(self.name.split('.')[0]+'_names.rs')

        for line in [x.replace('\n','').split(' ') for x in namefile.readlines()]:
            if line[0] == "input":
                inputs.append(line[1])
            elif line[0] == "output":
                outputs.append(line[1])

        # Create the file.
        handle = open(self.name.split('.')[0]+'_top.sv','w')

        # Declare top module.
        handle.write("module top (\n")

        for line in inputs[:-1]:
            handle.write('\tinput ' + line + ',\n')
        if len(outputs) != 0:
            if len(inputs) != 0: handle.write('\tinput ' + inputs[-1] + ',\n')
        else:
            if len(inputs) != 0: handle.write('\tinput ' + inputs[-1] + '\n')

        for line in outputs[:-1]:
            handle.write('\toutput ' + line + ',\n')
        if len(outputs) != 0: handle.write('\toutput ' + outputs[-1] + '\n')

        handle.write(");\n\n")

        # Write inst.
        handle.write(self.name.split('.')[0].split('/')[-1]+' inst_gen (\n')

        # Declare inputs
        for i,line in enumerate(self.inputs):
            if(len(inputs) > i):
                handle.write('\t.' + line + '(' + inputs[i] + '),\n')

        # Declare outputs
        for i,line in enumerate(self.outputs[:-1]):
            if(len(outputs) > i):
                handle.write('\t.' + line + '(' + outputs[i] + '),\n')
        handle.write('\t.' + self.outputs[-1] + '(' + outputs[len(self.outputs)-1] + ')\n')

        # Close inst.
        handle.write(');\n\nendmodule\n')

        handle.close()

