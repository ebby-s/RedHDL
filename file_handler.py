from mcpi.vec3 import Vec3

class FileHandler:

    def __init__(self, name):

        self.name = name

        self.inputs = []       # Input signals
        self.outputs = []      # Output signals
        self.signals = []      # Block signals

        self.signals_w = set() # Wire group signals
        self.signals_t = set() # Torch signals
        self.signals_f = set() # Flop internal signals
        self.signals_r = set() # Repeater signals
        self.signals_e = set() # Enable internal signals

        self.defs = {}         # Combinatorial internal signals
        self.torches = set()   # Definitions for torches
        self.flops = {}        # Sequential internal signals
        self.reps = set()      # Repeater signal definitions
        self.enables = {}      # Enables for repeaters

    def addInput(self, pos_string):
        self.inputs.append('i_'+pos_string)

    def addOutput(self, pos_string):
        self.outputs.append('o_'+pos_string)

    def addDeclr(self, pos_string):
        if pos_string[0] == 'w':
            self.signals_w.add(pos_string)
            self.defs[pos_string] = set()
        else:
            self.signals.append('p0_'+pos_string)
            self.defs['p0_'+pos_string] = set()

    def addDef(self, pos_string, line):
        self.defs[pos_string].add(line)

    def addTorch(self, pos_string, line):
        self.defs['p0_'+pos_string].add('(tr_'+pos_string+'<<2)')
        self.signals_t.add('tr_'+pos_string)
        self.torches.add(('tr_'+pos_string, line))

    def addFlop(self, pos_string, line, delay, loc):
        self.defs['p0_'+pos_string].add('(ff_'+pos_string+'<<2)')
        self.signals_f.add('ff_'+pos_string)
        if 'ff_'+pos_string in self.flops:
            self.flops['ff_'+pos_string].add((line, delay, loc))
        else:
            self.flops['ff_'+pos_string] = set([(line, delay, loc)])

    def addRep(self, pos_string, line, delay=0, loc=None):
        self.signals_r.add('rp_'+pos_string)
        self.reps.add(('rp_'+pos_string, line, delay, loc))

    def addEnable(self, pos_string, line, delay, loc):
        self.signals_e.add('en_'+pos_string)
        if 'en_'+pos_string in self.enables:
            self.enables['en_'+pos_string].add((line, delay, loc))
        else:
            self.enables['en_'+pos_string] = set([(line, delay, loc)])

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
        for group in [self.signals_w, self.signals_t, self.signals_f, self.signals_r, self.signals_e]:
            if len(group) != 0: handle.write(''.join(['\tlogic       '+sig+';\n' for sig in group]))

        # Assign combinatorial signals
        handle.write('\t// Assign internal signals.\n')
        for line in self.defs:
            handle.write('\tassign '+line+' = '+(' | '.join(self.defs[line]) if len(self.defs[line]) != 0 else '0')+';\n')
        handle.write('\n')

        # Make torches
        if len(self.torches) != 0:
            handle.write('\t// Make torches.\n')
            handle.write('\talways_ff @(posedge clk) begin\n')
            handle.write(''.join(['\t\t'+torch+' <= '+line+';\n' for torch,line in self.torches]))
            handle.write('\tend\n\n')

        # Make flops
        handle.write('\t// Make flops.\n')
        for flop in self.flops:

            for i,line in enumerate(self.flops[flop]):
                handle.write('\tlogic ['+str(line[1]-1)+':0] '+flop+'_'+str(i)+'_delay;\n')
                handle.write('\tlogic       '+flop+'_'+str(i)+'_in;\n')

            handle.write('\n\tassign '+flop+' = '+' | '.join([flop+'_'+str(i)+'_delay[0]' for i in range(len(self.flops[flop]))])+';\n\n')
            handle.write(''.join(['\tassign '+flop+'_'+str(i)+'_in = '+line[0]+';\n' for i,line in enumerate(self.flops[flop])]))

            handle.write('\n\talways_ff @(posedge clk) begin\n')
            for i,line in enumerate(self.flops[flop]):
                if line[1] == 1:
                    write_line = flop+'_'+str(i)+'_delay <= '+flop+'_'+str(i)+'_in;\n'
                else:
                    write_line = flop+'_'+str(i)+'_delay <= {'+flop+'_'+str(i)+'_in, '+flop+'_'+str(i)+'_delay['+str(line[1]-1)+':1]};\n'

                if 'en_'+line[2] in self.signals_e:
                    handle.write('\t\tif (~en_'+line[2]+') begin\n')
                    handle.write('\t\t\t'+write_line)
                    handle.write('\t\tend\n')
                else:
                    handle.write('\t\t'+write_line)
            handle.write('\tend\n\n')

        # Make series repeaters
        handle.write('\n\t// Make series repeaters.\n')

        reps_comb = [rep for rep in self.reps if rep[2] == 0]
        reps_flop = [rep for rep in self.reps if rep[2] == 1]
        reps_vari = [rep for rep in self.reps if rep[2]  > 1]

        if len(reps_comb) != 0:
            handle.write(''.join(['\tassign '+line[0]+' = '+line[1]+';\n' for line in reps_comb])+'\n')

        if len(reps_flop) != 0:
            handle.write('\talways_ff @(posedge clk) begin\n')
            for rep,line,delay,loc in reps_flop:
                if 'en_'+loc in self.signals_e:
                    handle.write('\t\tif (~en_'+loc+') begin\n')
                    handle.write('\t\t\t'+rep+' <= '+line+';\n')
                    handle.write('\t\tend\n')
                else:
                    handle.write('\t\t'+rep+' <= '+line+';\n')
            handle.write('\tend\n\n')

        if len(reps_vari) != 0:
            handle.write(''.join(['\tlogic ['+str(line[2]-1)+':0] '+line[0]+'_delay;\n' for line in reps_vari])+'\n')
            handle.write(''.join(['\tassign '+line[0]+' = '+line[0]+'_delay[0];\n' for line in reps_vari])+'\n')

            handle.write('\talways_ff @(posedge clk) begin\n')
            for rep,line,delay,loc in reps_vari:
                if 'en_'+loc in self.signals_e:
                    handle.write('\t\tif (~en_'+loc+') begin\n')
                    handle.write('\t\t\t'+rep+'_delay <= {'+line+', '+rep+'_delay['+str(delay-1)+':1]};\n')
                    handle.write('\t\tend\n')
                else:
                    handle.write('\t\t'+rep+'_delay <= {'+line+', '+rep+'_delay['+str(delay-1)+':1]};\n')
            handle.write('\tend\n\n')
        
        # Make enables
        handle.write('\t// Make enables.\n')
        for enable in self.enables:

            for i,line in enumerate(self.enables[enable]):
                handle.write('\tlogic ['+str(line[1]-1)+':0] '+enable+'_'+str(i)+'_delay;\n')
                handle.write('\tlogic       '+enable+'_'+str(i)+'_in;\n')

            handle.write('\n\tassign '+enable+' = '+' | '.join([enable+'_'+str(i)+'_delay[0]' for i in range(len(self.enables[enable]))])+';\n\n')
            handle.write(''.join(['\tassign '+enable+'_'+str(i)+'_in = '+line[0]+';\n' for i,line in enumerate(self.enables[enable])]))

            handle.write('\n\talways_ff @(posedge clk) begin\n')
            for i,line in enumerate(self.enables[enable]):
                if line[1] == 1:
                    write_line = enable+'_'+str(i)+'_delay <= '+enable+'_'+str(i)+'_in;\n'
                else:
                    write_line = enable+'_'+str(i)+'_delay <= {'+enable+'_'+str(i)+'_in, '+enable+'_'+str(i)+'_delay['+str(line[1]-1)+':1]};\n'

                if 'en_'+line[2] in self.signals_e:
                    handle.write('\t\tif (~en_'+line[2]+') begin\n')
                    handle.write('\t\t\t'+write_line)
                    handle.write('\t\tend\n')
                else:
                    handle.write('\t\t'+write_line)
            handle.write('\tend\n\n')

        # Assign outputs
        handle.write('\t// Assign output signals.\n')
        handle.write(''.join(['\tassign '+line+' = |p0'+line[1:]+';\n' for line in self.outputs]))

        # End definiton and close file.
        handle.write('\n\nendmodule\n')
        handle.close()

        self.writeInstFile()


    def writeInstFile(self):

        # Read names ofclock, inputs and outputs.
        inputs = []
        outputs = []
        clk_name = ''

        try:
            namefile = open(self.name.split('.')[0]+'_names.rs')

            for line in [x.replace('\n','').split(' ') for x in namefile.readlines()]:
                if line[0] == "input":
                    inputs.append(line[1])
                elif line[0] == "output":
                    outputs.append(line[1])
                elif line[0] == "clock":
                    clk_name = line[1]
        except:
            return

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

