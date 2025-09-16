import re
import sys
import os

#ran with py .\P2. File.ll
def parser(filename):
    with open(filename, 'r') as f:
        content = f.read()

        file_functs = []
        #this re stuff is pretty neato
        funct_finder = re.findall(r'define[^{]*\{(.*?)\}', content, re.DOTALL)

        #break it down
        for i in funct_finder:
            blocks = get_blocks(i)
            cfg = make_cfg(blocks)
            file_functs.append((cfg, blocks))

        return file_functs
    
def get_blocks(body):
    blocks = {}
    lines = [line.strip() for line in body.split('\n') if line.strip()]
    
    curr_block = []
    curr_label = 'entry'
    #finding llvm blocks
    for i in lines:
        if i.endswith(':'):
            if curr_block:
                blocks[curr_label] = curr_block
            curr_label = i[:-1]
            curr_block = []
        else:
            curr_block.append(i)

    if curr_block:
        blocks[curr_label] = curr_block
    return blocks

def make_cfg(blocks):
    cfg = {}
    block_names = list(blocks.keys())

    for i, (name, instructions) in enumerate(blocks.items()):
        cfg[name] = []
        if instructions:
            last_instr = instructions[-1]
            #conditional branch
            if last_instr.startswith('br i1'):
                two_dests = re.findall(r'label %(\w+)', last_instr)
                cfg[name].append((two_dests[0], 0))
                cfg[name].append((two_dests[1], 1))
            #non conditional branch
            elif last_instr.startswith('br label'):
                dest = re.search(r'label %(\w+)', last_instr)
                if dest:
                    cfg[name].append((dest.group(1), 0))

            #other
            elif not last_instr.startswith('ret ') and i + 1 < len(block_names):
                cfg[name].append((block_names[i+1], 0))

    return cfg

def dot_funct(functs):
    output = []

    for funct_idx, (cfg, blocks) in enumerate(functs):
        output.append("digraph {")
        #output.append("    node [shape=record];"), now in node like example

        node_map = {name: f"Node{idx}" for idx, name in enumerate(blocks.keys())}

        #nodes
        for name, node_id in node_map.items():
            output.append(f'    {node_id} [shape=record,label="{name}"];')
            #I assumed record ment like, a record, circular, I guess not?
        #edges
        for src, targets in cfg.items():
            for target, edge_label in targets:
                if target in node_map:
                    output.append(f'    {node_map[src]} -> {node_map[target]} [label="{edge_label}"];')

        output.append("}\n")
    return "\n".join(output)

def main():
    input_file = sys.argv[1]
    output_file = os.path.splitext(input_file)[0] +".dot"

    functions = parser(input_file)
    dot_out = dot_funct(functions)

    with open(output_file, 'w') as f:
        f.write(dot_out)



main()
