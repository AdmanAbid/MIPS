OP_TO_CODE = {
    'beq'  : 0,
    'add'  : 1,
    'nor'  : 2,
    'or'   : 3,
    'addi' : 4,
    'sll'  : 5,
    'sw'   : 6,
    'sub'  : 7,
    'j'    : 8,
    'and'  : 9,
    'srl'  : 10,
    'ori'  : 11,
    'bneq' : 12,
    'subi' : 13,
    'andi' : 14,
    'lw'   : 15
}

REGISTER_TO_CODE = {
    '$zero' : 0,
    '$t0'   : 1,
    '$t1'   : 2,
    '$t2'   : 3,
    '$t3'   : 4,
    '$t4'   : 5,
    '$sp'   : 6,
}

def normalize_line(line):
    code_only = line.split('#', 1)[0]
    return code_only.strip().replace(',', ' ')


def tokenize_line(line):
    normalized = normalize_line(line)
    if not normalized:
        return []
    return normalized.split()


def parse_memory_operand(operand):
    offset_str, rs_str = operand.split('(')
    offset = int(offset_str)
    rs = rs_str.rstrip(')')
    return offset, rs


def load_lines(path):
    with open(path, "r") as f:
        return f.readlines()
    

def init_sp(lines):
    return ["addi $sp, $zero, 15"] + lines


def expand_pseudo_instructions(lines):
    expanded_lines = []

    for line in lines:
        tokens = tokenize_line(line)
        if not tokens:
            expanded_lines.append(line)
            continue

        op = tokens[0]
        if op == 'push' and len(tokens) == 2:
            reg = tokens[1]
            expanded_lines.append(f"sw {reg}, 0($sp)\n")
            expanded_lines.append("addi $sp, $sp, -1\n")
        elif op == 'pop' and len(tokens) == 2:
            reg = tokens[1]
            expanded_lines.append("addi $sp, $sp, 1\n")
            expanded_lines.append(f"lw {reg}, 0($sp)\n")
        else:
            expanded_lines.append(line)

    return expanded_lines


def build_symbol_table(lines):
    symbol_table = {}
    instruction_count = 0

    for line in lines:
        tokens = tokenize_line(line)
        if not tokens:
            continue

        first = tokens[0]
        if first.endswith(':'):
            label = first[:-1]
            symbol_table[label] = instruction_count
        else:
            instruction_count += 1

    return symbol_table


def generate_r_type(op, rd, rs, rt):
    op_code = OP_TO_CODE[op]
    rd_code = REGISTER_TO_CODE[rd]
    rs_code = REGISTER_TO_CODE[rs]
    rt_code = REGISTER_TO_CODE[rt]

    instr = (op_code << 12) | (rs_code << 8) | (rt_code << 4) | rd_code
    return instr

def generate_s_type(op, rd, rs, shamt):
    op_code = OP_TO_CODE[op]
    rd_code = REGISTER_TO_CODE[rd]
    rs_code = REGISTER_TO_CODE[rs]

    instr = (op_code << 12) | (rs_code << 8) | (rd_code << 4) | shamt

    return instr

def generate_i_type(op, rs, rd_or_rs2, imm_or_offset):
    op_code = OP_TO_CODE[op]
    rd_or_rs2_code = REGISTER_TO_CODE[rd_or_rs2]
    rs_code = REGISTER_TO_CODE[rs]

    imm_or_offset &= 0xF

    instr = (op_code << 12) | (rs_code << 8) | (rd_or_rs2_code << 4) | imm_or_offset

    return instr

def generate_j_type(op, jump_address):
    op_code = OP_TO_CODE[op]

    instr = (op_code << 12) | (jump_address << 4)

    return instr

def generate_machine_code(tokens, instruction_count):
    op = tokens[0]

    if op in {'add', 'sub', 'and', 'or', 'nor'}:
        return generate_r_type(op, tokens[1], tokens[2], tokens[3])
    elif op in {'addi', 'subi', 'andi', 'ori'}:
        return generate_i_type(op, tokens[2], tokens[1], int(tokens[3]))
    elif op in {'sll', 'srl'}:
        return generate_s_type(op, tokens[1], tokens[2], int(tokens[3]))
    elif op == 'lw':
        rd = tokens[1]
        offset, rs = parse_memory_operand(tokens[2])
        return generate_i_type(op, rs, rd, offset)
    elif op == 'sw':
        rs2 = tokens[1]
        offset, rs = parse_memory_operand(tokens[2])
        return generate_i_type(op, rs, rs2, offset)
    elif op in {'beq', 'bneq'}:
        rs = tokens[1]
        rt = tokens[2]
        label = tokens[3]
        label_instruction_count = symbol_table[label]
        offset = label_instruction_count - (instruction_count + 1)
        return generate_i_type(op, rs, rt, offset)
    elif op == 'j':
        return generate_j_type(op, symbol_table[tokens[1]])

    return None


def assemble(lines):
    ops = []
    instruction_count = 0

    for line in lines:
        tokens = tokenize_line(line)
        if not tokens:
            continue

        first = tokens[0]
        if first.endswith(':'):
            continue

        ops.append(generate_machine_code(tokens, instruction_count))
        instruction_count += 1

    return ops


def print_ops(ops):
    for instr in ops:
        bin_str = f"{instr:016b}"
        chunks = [bin_str[i:i+4] for i in range(0, 16, 4)]
        print(' ||| '.join(chunks))


def write_binary_output(ops, path):
    with open(path, 'wb') as f:
        for instr in ops:
            f.write(instr.to_bytes(2, byteorder='big'))


if __name__ == "__main__":
    lines = load_lines("input.asm")
    lines = init_sp(lines)
    lines = expand_pseudo_instructions(lines)
    symbol_table = build_symbol_table(lines)
    ops = assemble(lines)
    print_ops(ops)

    write_binary_output(ops, 'out.bin')
    print("Complete!")
    