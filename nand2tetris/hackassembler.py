#HEADERS
import fileinput, sys

#FUNCTIONS

def error(msg):
	raw_input('ERROR: ' + msg)
	sys.exit()

class Parser:
	def __init__(self):
		self.code_comp = {
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
			
		self.code_dest = {
			'null' : "000" ,
			'M'    : "001" ,
			'D'    : "010" ,
			'MD'   : "011" ,
			'A'    : "100" ,
			'AM'   : "101" ,
			'AD'   : "110" ,
			'AMD'  : "111" }
			
		self.code_jump = {
			'null' : "000" ,
			'JGT'  : "001" ,
			'JEQ'  : "010" ,
			'JGE'  : "011" ,
			'JLT'  : "100" ,
			'JNE'  : "101" ,
			'JLE'  : "110" ,
			'JMP'  : "111" }
			
		self.symboltable = {
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
			
	def _strip(self, line):
		return line.partition('//')[0].strip()
		
	def _is_label(self, line):
		if line[0] == '(' and line[-1] == ')': return True
		
	def _is_symbol(self, line):
		if line[0] == '@' and not line[1:].isdigit(): return True
		
	def _code(self, comp, dest, jump):
		if len(dest) == 0: dest = 'null'
		if len(jump) == 0: jump = 'null'
		comp = self.code_comp[comp.replace(' ','')]
		dest = self.code_dest[dest.replace(' ','')]
		jump = self.code_jump[jump.replace(' ','')]
		return comp + dest + jump
			
	def build_symbol_table(self, file):
		linenumber = 0
		symbols = []
		for line in file:
			line = self._strip(line)
			if len(line) > 0:
				if self._is_label(line):
					line = line.strip('()')
					if self.symboltable.has_key(line): error('Duplicate label ' + line)
					else: self.symboltable[line] = linenumber
				else:
					if self._is_symbol(line):
						line = line[1:]
						if line not in symbols: symbols.append(line)
					linenumber += 1
					
		nextmem = 16
		for symbol in symbols:
			if symbol not in self.symboltable:
				self.symboltable[symbol] = nextmem
				nextmem += 1
				
	def parse(self, file):
		lines = []
		for line in file:
			line = self._strip(line)
			if len(line) > 0:
				#A-instruction
				if line[0] == '@':
					i = 0
					if line[1:].isdigit():
						i = int(line[1:]) % (2**15)
					else:
						i = self.symboltable[line[1:]]
					lines.append('0' + bin(i)[2:].zfill(15) + '\n')
				#C-Instruction
				elif not self._is_label(line):
					(line, sep, jump) = line.partition(';')
					(dest, sep, comp) = line.rpartition('=')
					lines.append('111' + self._code(comp,dest,jump) + '\n')
		return lines
	
def get_file_input():
	filename = raw_input('Filename:')
	file = open(sys.path[0] + '\\' + filename + '.asm','r')
	return file, filename
	
if __name__ == '__main__':
	(file, filename) = get_file_input()
	parser = Parser()
	parser.build_symbol_table(file)
	file.seek(0)
	parsed = parser.parse(file)
	f = open(sys.path[0] + '\\' + filename + '.hack', 'w')
	f.writelines(parsed)

	
	raw_input('Continue...')
#EOS