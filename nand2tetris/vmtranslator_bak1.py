import fileinput, sys
	
#classes
def error(msg):
	raw_input('ERROR: ' + msg)
	sys.exit()
	
class C_Base():
	def __init__(self, linenumber, id, arg1=None, arg2=None):
		self.linenumber = linenumber
		self.id = id
		self.arg1 = arg1
		self.arg2 = arg2
	def getcodelist(self, currentline):
		
		
class C_Arithmetic(C_Base):
	def getcodelist(self):
		
		
	
class C_Push(C_Base):
	def __init__(self, command, arg1, arg2):
		self.command = command
		self.arg1 = arg1
		self.arg2 = arg2

class C_Pop(C_Base):
	def __init__(self, command, arg1, arg2):
		self.command = command
		self.arg1 = arg1
		self.arg2 = arg2
	
class C_Label(C_Base):
	pass
	
class C_Goto(C_Base):
	pass

class C_If(C_Base):
	pass
	
class C_Function(C_Base):
	pass
	
class C_Return(C_Base):
	pass
	
class C_Call(C_Base):
	pass

class Parser():
	_commands = {
		'add' = C_Arithmetic,
		'sub' = C_Arithmetic,
		'neg' = C_Arithmetic,
		'eq' = C_Arithmetic,
		'gt' = C_Arithmetic,
		'lt' = C_Arithmetic,
		'and' = C_Arithmetic,
		'or' = C_Arithmetic,
		'not' = C_Arithmetic,
		
		'push' = C_Push,
		'pop' = C_Pop,
	}

	def _tokenize(self, line):
		r1, r2, r3 = line.partition('//')[0].split(maxsplit=2)
		return r1, r2, r3

	def parse(self, file):
		parsed = []
		linenumber, count = 0, 0
		for line in file:
			linenumber += 1
			id, arg1, arg2 = self._tokenize(line)
			if id in _commands:
				parsed[count] = _commands[id](linenumber, id, arg1, arg2)
				count += 1
		return parsed
		
class Coder():
	_codes = {
		'add': [
			lambda x: '@SP'		,
			lambda x: 'AM=M-1'	,
			lambda x: 'D=M'		,
			lambda x: '@SP'		,
			lambda x: 'A=M-1'	,
			lambda x: 'M=D+M'	]
		,
		'sub': [
			lambda x: '@SP'		,
			lambda x: 'AM=M-1'	,
			lambda x: 'D=M'		,
			lambda x: '@SP'		,
			lambda x: 'A=M-1'	,
			lambda x: 'M=M-D'	]
		,
		'neg': [
			lambda x: '@SP'		,
			lambda x: 'A=M-1'	,
			lambda x: 'M=-M'	]
		,
		'eq': [
			lambda x: '@SP'		,
			lambda x: 'AM=M-1'	,
			lambda x: 'D=M'		,
			lambda x: '@SP'		,
			lambda x: 'A=M-1'	,
			lambda x: 'D=M-D'	,
			lambda x: '@'+(x+2)	,
			lambda x: 'D;JEQ'	,
			lambda x: 'D=-1'	,
			lambda x: '@SP'		,
			lambda x: 'A=M-1'	,
			lambda x: 'M=!D'	]
		,
		'gt': [
			lambda x: '@SP'		,
			lambda x: 'AM=M-1'	,
			lambda x: 'D=M'		,
			lambda x: '@SP'		,
			lambda x: 'A=M-1'	,
			lambda x: 'D=M-D'	,
			lambda x: '@-32768'	,
			lambda x: 'D=D&A'	,
			lambda x: '@'+(x+2)	,
			lambda x: 'D;JEQ'	,
			lambda x: 'D=-1'	,
			lambda x: '@SP'		,
			lambda x: 'M=!D'	]
		,
		'lt': [
			lambda x: '@SP'		,
			lambda x: 'AM=M-1'	,
			lambda x: 'D=M'		,
			lambda x: '@SP'		,
			lambda x: 'A=M-1'	,
			lambda x: 'D=D-M'	,
			lambda x: '@-32768'	,
			lambda x: 'D=D&A'	,
			lambda x: '@'+(x+2)	,
			lambda x: 'D;JEQ'	,
			lambda x: 'D=-1'	,
			lambda x: '@SP'		,
			lambda x: 'M=!D'	]
		,
		'and': [
			lambda x: '@SP'		,
			lambda x: 'AM=M-1'	,
			lambda x: 'D=M'		,
			lambda x: '@SP'		,
			lambda x: 'A=M-1'	,
			lambda x: 'M=D&M'	]
		,
		'or': [
			lambda x: '@SP'		,
			lambda x: 'AM=M-1'	,
			lambda x: 'D=M'		,
			lambda x: '@SP'		,
			lambda x: 'A=M-1'	,
			lambda x: 'M=D|M'	]
		,
		'not': [
			lambda x: '@SP'		,
			lambda x: 'A=M-1'	,
			lambda x: 'M=!M'		]
	}
	
	def code(self, parsed):
		coded = []
		i = 0
		for command in parsed:
			codelist, count = command.getcodelist(i)
			coded[i:i+count-1] = codelist
			i = i + count
		return coded
			

if __name__ == "__main__":
	parser, coder = Parser(), Coder()
	
	#get file
	filename = raw_input('Filename:')
	file = open(sys.path[0] + '\\' + filename + '.vm','r')
	
	#get parsed list
	parsed = parser.parse(file)
	coded = coder.code(parsed)
	
	#open new file
	file = open(sys.path[0] + '\\' + filename + '.asm', 'w')
	file.writelines(coded)
	
	#write to new file