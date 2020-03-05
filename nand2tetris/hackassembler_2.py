import sys
from enum import Enum


class CommandType(Enum):
    A = 1
    C = 2
    L = 3


class SymbolError(Exception):
    pass

class CommandError(Exception):
    pass


class Parser:
    def __init__(self, file):
        self.buffer = file

    def has_more_commands(self):
        pos = self.buffer.tell()
        if self.buffer.readline():
            self.buffer.seek(pos)
            return True
        else:
            self.buffer.seek(pos)
            return False

    def reset(self):
        self.buffer.seek(0)
        self.current_command = None

    def advance(self):
        while True:
            line = self.buffer.readline()
            if not line: break
            line = line.partition('//')[0].strip()
            if line: break
        self.current_command = line

    def get_command_type(self):
        if self.current_command[0] == '@':
            s = self.current_command[1:]
            if s.isdigit() or self.is_valid_symbol(s):
                return CommandType.A
            else:
                raise SymbolError(s)

        elif self.current_command[0] == '(' and self.current_command[-1] == ')':
            if self._is_valid_symbol(self.current_command[1:-1]):
                return CommandType.L
            else:
                raise SymbolError(self.current_command[1:-1])

        else:
            return CommandType.C

    _validcharlist = {'_', '.', '$', ':'}

    def is_valid_symbol(self, symbol):
        if symbol[0].isdigit():
            return False
        for c in symbol:
            if not c.isalnum() and c not in _validcharlist:
                return False
        return True

    def get_symbol(self):
        t = self.get_command_type()
        if t == CommandType.A: return self.current_command[1:]
        elif t == CommandType.L: return self.current_command[1:-1]

    def getDest(self):
        #return dest mnemonic of C_COMMAND
        pass

    def getComp(self):
        #comp mnemonic of C_COMMAND
        pass

    def getJump(self):
        #jump mnemonic of C_COMMAND
        pass


class Code:
    code_dest = {
        '' : "000" ,
        'M'    : "001" ,
        'D'    : "010" ,
        'MD'   : "011" ,
        'A'    : "100" ,
        'AM'   : "101" ,
        'AD'   : "110" ,
        'AMD'  : "111" }

    code_comp = {
        #D,A computation
        '0'   :	"0101010" ,
        '1'   :	"0111111" ,
        '-1'  :	"0111010" ,
        'D'   :	"0001100" ,
        'A'   :	"0110000" ,
        '!D'  :	"0001101" ,
        '!A'  :	"0110001" ,
        '-D'  :	"0001111" ,
        '-A'  :	"0110011" ,
        'D+1' :	"0011111" ,
        'A+1' :	"0110111" ,
        'D-1' :	"0001110" ,
        'A-1' :	"0110010" ,
        'D+A' :	"0000010" ,
        'D-A' :	"0010011" ,
        'A-D' :	"0000111" ,
        'D&A' :	"0000000" ,
        'D|A' :	"0010101" ,
        #D,M computation
        'M'   :	"1110000" ,
        '!M'  :	"1110001" ,
        '-M'  :	"1110011" ,
        'M+1' :	"1110111" ,
        'M-1' :	"1110010" ,
        'D+M' :	"1000010" ,
        'D-M' :	"1010011" ,
        'M-D' :	"1000111" ,
        'D&M' :	"1000000" ,
        'D|M' :	"1010101" }

    code_jump = {
        '' : "000" ,
        'JGT'  : "001" ,
        'JEQ'  : "010" ,
        'JGE'  : "011" ,
        'JLT'  : "100" ,
        'JNE'  : "101" ,
        'JLE'  : "110" ,
        'JMP'  : "111" }

    def dest(self, c):
        return self.code_dest[c]

    def comp(self, c):
        return self.code_comp[c]

    def jump(self, c):
        return self.code_jump[c]


class SymbolTable:
    def __init__ (self):
        self.symbols = {
			'SP'     : 0     ,
			'LCL'    : 1     ,
			'ARG'    : 2     ,
			'THIS'   : 3     ,
			'THAT'   : 4     ,
			'R0'     : 0     ,
			'R1'     : 1     ,
			'R2'     : 2     ,
			'R3'     : 3     ,
			'R4'     : 4     ,
			'R5'     : 5     ,
			'R6'     : 6     ,
			'R7'     : 7     ,
			'R8'     : 8     ,
			'R9'     : 9     ,
			'R10'    : 10    ,
			'R11'    : 11    ,
			'R12'    : 12    ,
			'R13'    : 13    ,
			'R14'    : 14    ,
			'R15'    : 15    ,
			'SCREEN' : 16384 ,
			'KBD'    : 24576 }

    def add_entry(self, symbol, address):
        self.symbols[symbol] = address

    def contains(self, symbol):
        return symbol in self.symbols

    def get_address(self, symbol):
        return self.symbols[symbol]


def get_file_input():
    filename = input('Filename:')
    filepath = sys.path[0] + '\\' + filename + '.asm'
    file = open(filepath,'r')
    if file:
        return file, filename
    else:
        raise Exception(filepath)

if __name__ == "__main__":
    (file, filename) = get_file_input()
    parser = Parser(file)
    symboltable = SymbolTable()

    #first pass, get symbols
    data_addr = 16
    inst_count = 0
    varsymbols = []
    while parser.has_more_commands():
        parser.advance()
        commandtype = parser.get_command_type()
        if commandtype == CommandType.L:
            symbol = parser.get_symbol()
            if not symboltable.contains(symbol):
                symboltable.add_entry(symbol, inst_count)
        else:
            if commandtype == CommandType.A:
                symbol = parser.get_symbol()
                if not symbol.isdigit():
                    varsymbols.append(symbol)
            inst_count+=1
    for symbol in varsymbols:
        if not symboltable.contains(symbol):
            symboltable.add_entry(symbol, data_addr)
            data_addr+=1

    parser.reset()
    code = Code()
    codedlist = []
    while parser.has_more_commands():
        parser.advance()
        commandtype = parser.get_command_type()
        if commandtype == CommandType.A:
            val = parser.get_symbol()
            if val.isdigit():
                val = int(val) % (2**15)
            else:
                val = symboltable.symbols[val]
            codedlist.append('0' + bin(val)[2:].zfill(15))
        elif commandtype == CommandType.C:
            c = parser.current_command
            (c, sep, jump) = c.partition(';')
            (dest, sep, comp) = c.rpartition('=')
            codedlist.append('111' + code.comp(comp) + code.dest(dest) + code.jump(jump))

    objectcode = '\n'.join(codedlist)
    print(objectcode)
