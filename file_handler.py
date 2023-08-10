from mcpi.vec3 import Vec3

class FileHandler:

    def __init__(self, name):

        self.name = name

        self.inputs = []
        self.outputs = []
        self.signals = []
        self.signals_w = []

        self.defs = {}
        self.latched = {}

    def addInput(self, pos_string):
        self.inputs.append('i_' + pos_string)

    def addOutput(self, pos_string):
        self.outputs.append('o_' + pos_string)

    def addDeclr(self, pos_string):
        if pos_string[-1] == 'w':
            self.signals_w.append('p0_' + pos_string)
        else:
            self.signals.append('p0_' + pos_string)
        self.defs['p0_' + pos_string] = set()

    def addDef(self, pos_string, line):
        if ('p0_' + pos_string) in self.defs.keys():
            self.defs['p0_' + pos_string].add(line)
        else:
            self.latched['p0_' + pos_string][1].add(line)

    def addLatch(self, pos_string, line):
        if ('p0_' + pos_string) in self.latched.keys():
            self.latched['p0_' + pos_string][0].add(line)
        else:
            self.latched['p0_' + pos_string] = (set([line]), self.defs['p0_' + pos_string])
            self.defs.pop('p0_' + pos_string, None)

    def writeFile(self):

        # Create the output file.
        handle = open(self.name,'w')

        # Open header
        handle.write('module '+self.name.split('.')[0].split('/')[-1]+' (\n')
        # Declare clocks
        handle.write('\t// Declare clocks.\n')
        handle.write('\tinput  logic clk')
        handle.write(',\n' if (len(self.outputs) != 0) or (len(self.inputs) != 0) else '\n')
        # Declare inputs
        handle.write('\t// Declare input signals.\n')
        handle.write('\tinput  logic ' + ',\n\tinput  logic '.join(self.inputs))
        handle.write(',\n' if (len(self.outputs) != 0) and (len(self.inputs) != 0) else '\n')
        # Declare outputs
        handle.write('\t// Declare output signals.\n')
        handle.write('\toutput logic ' + ',\n\toutput logic '.join(self.outputs))
        # Close header
        handle.write('\n);\n\n')

        # Declare internal signals
        handle.write('\t// Declare internal signals.\n')
        handle.write('\tlogic [2:0] ' + ';\n\tlogic [2:0] '.join(self.signals) + ';\n')
        handle.write('\tlogic       ' + ';\n\tlogic       '.join(self.signals_w) + ';\n\n')

        # Assign combinatorial signals
        handle.write('\t// Assign internal signals.\n')
        for line in self.defs:
            handle.write('\tassign ' + line + ' = ')
            handle.write(' | '.join(self.defs[line]) if len(self.defs[line]) != 0 else '0')
            handle.write(';\n')

        # Assign latches
        handle.write('\n\t// Assign latches.\n')
        for line in self.latched:
            handle.write('\talways_ff @(posedge clk) begin\n')
            handle.write('\t\tif (' + ' || '.join(self.latched[line][0]) + ') begin\n')
            handle.write('\t\t\t' + line + ' = ' + ' | '.join(self.latched[line][1]) + ';\n')
            handle.write('\t\tend\n' + '\tend\n\n')

        # Assign outputs
        handle.write('\t// Assign output signals.\n' + '\tassign ')
        handle.write(';\n\tassign '.join([(line+' = |p0'+line[1:]) for line in self.outputs])+';')

        # End definiton and close file.
        handle.write('\n\nendmodule\n')
        handle.close()

        self.writeInstFile()


    def writeInstFile(self):

        # Read names ofclock, inputs and outputs.
        inputs = []
        outputs = []
        clk_name = ''

        namefile = open(self.name.split('.')[0]+'_names.rs')

        for line in [x.replace('\n','').split(' ') for x in namefile.readlines()]:
            if line[0] == "input":
                inputs.append(line[1])
            elif line[0] == "output":
                outputs.append(line[1])
            elif line[0] == "clock":
                clk_name = line[1]

        # Create the file.
        handle = open(self.name.split('.')[0]+'_top.sv','w')

        # Open header
        handle.write('module top (\n')
        # Declare clocks
        handle.write('\tinput  logic ' + clk_name)
        handle.write(',\n' if (len(outputs) != 0) or (len(inputs) != 0) else '\n')
        # Declare inputs
        handle.write('\tinput  logic ' + ',\n\tinput  logic '.join(inputs))
        handle.write(',\n' if (len(outputs) != 0) and (len(inputs) != 0) else '\n')
        # Declare outputs
        handle.write('\toutput logic ' + ',\n\toutput logic '.join(outputs))
        # Close header
        handle.write('\n);\n\n')

        # Write inst.
        handle.write(self.name.split('.')[0].split('/')[-1]+' inst_gen (\n')

        handle.write('\t.clk(' + clk_name + '),\n')

        # Declare inputs and outputs
        n_inputs = min(len(self.inputs), len(inputs))
        n_outputs = min(len(self.outputs), len(outputs))

        handle.write('\t.')
        handle.write('),\n\t.'.join([self.inputs[i]+'('+inputs[i] for i in range(n_inputs)]) + ')')
        handle.write(',\n' if (n_outputs != 0) and (n_inputs != 0) else '\n')

        handle.write('\t.')
        handle.write('),\n\t.'.join([self.outputs[i]+'('+outputs[i] for i in range(n_outputs)]) + ')')

        # Close inst. and close file
        handle.write('\n);\n\nendmodule\n')
        handle.close()

