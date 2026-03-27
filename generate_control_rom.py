from dataclasses import dataclass


# [15:13] ALUOP (3)
# [12]    RegWrite
# [11]    RegDst
# [10]    ALUsrc
# [9]     Memwrite
# [8]     Memread
# [7]     MemtoReg
# [6]     bneq
# [5]     branch
# [4]     jump
# [3:0]   unused (0)

# -------------------------
# ALU operation encodings
# -------------------------
ALU = {
    "add": 0b000,
    "sub": 0b001,
    "and": 0b010,
    "or":  0b011,
    "nor": 0b100,
    "sll": 0b101,
    "srl": 0b110,
}

# -------------------------
# Control Word Dataclass
# -------------------------
@dataclass
class ControlWord:
    ALUOP: int = 0
    RegWrite: int = 0
    RegDst: int = 0
    ALUsrc: int = 0
    Memwrite: int = 0
    Memread: int = 0
    MemtoReg: int = 0
    bneq: int = 0
    branch: int = 0
    jump: int = 0

    def encode(self) -> int:
        value = 0
        value |= (self.ALUOP & 0b111) << 13
        value |= (self.RegWrite & 1) << 12
        value |= (self.RegDst & 1) << 11
        value |= (self.ALUsrc & 1) << 10
        value |= (self.Memwrite & 1) << 9
        value |= (self.Memread & 1) << 8
        value |= (self.MemtoReg & 1) << 7
        value |= (self.bneq & 1) << 6
        value |= (self.branch & 1) << 5
        value |= (self.jump & 1) << 4
        return value


# -------------------------
# Define All Instructions
# -------------------------

control_rom = {}

# Opcode mapping you provided
opcode_map = {
    0: "N",   # beq
    1: "A",   # add
    2: "K",   # nor
    3: "G",   # or
    4: "B",   # addi
    5: "I",   # sll
    6: "M",   # sw
    7: "C",   # sub
    8: "P",   # j
    9: "E",   # and
    10: "J",  # srl
    11: "H",  # ori
    12: "O",  # bneq
    13: "D",  # subi
    14: "F",  # andi
    15: "L",  # lw
}

# Helper constructors

R_TYPE = lambda alu: ControlWord(ALUOP=ALU[alu], RegWrite=1, RegDst=1)
I_ARITH = lambda alu: ControlWord(ALUOP=ALU[alu], RegWrite=1, RegDst=0, ALUsrc=1)
LOAD = ControlWord(ALUOP=ALU["add"], RegWrite=1, RegDst=0, ALUsrc=1, Memread=1, MemtoReg=1)
STORE = ControlWord(ALUOP=ALU["add"], ALUsrc=1, Memwrite=1)
BEQ = ControlWord(ALUOP=ALU["sub"], branch=1)
BNE = ControlWord(ALUOP=ALU["sub"], branch=1, bneq=1)
JUMP = ControlWord(jump=1)

# Fill control words

instruction_controls = {
    "A": R_TYPE("add"),
    "C": R_TYPE("sub"),
    "E": R_TYPE("and"),
    "G": R_TYPE("or"),
    "K": R_TYPE("nor"),
    
    "I": I_ARITH("sll"),
    "J": I_ARITH("srl"),

    "B": I_ARITH("add"),
    "D": I_ARITH("sub"),
    "F": I_ARITH("and"),
    "H": I_ARITH("or"),

    "L": LOAD,
    "M": STORE,

    "N": BEQ,
    "O": BNE,

    "P": JUMP,
}

# -------------------------
# Generate ROM Binary
# -------------------------

rom_words = []

for opcode in range(16):
    instr_id = opcode_map[opcode]
    cw = instruction_controls[instr_id]
    encoded = cw.encode()
    rom_words.append(encoded)

# Write raw binary file
with open("control_rom.bin", "wb") as f:
    for word in rom_words:
        f.write(word.to_bytes(2, byteorder="big"))

print("Control ROM generated.")