import fileinput, sys, os
	
def error(msg):
	raw_input('ERROR: ' + msg)
	sys.exit()
	
commands_arithmetic = {
	'add': [
		'@SP'		,
		'AM=M-1'	,
		'D=M'		,
		'A=A-1'		,
		'M=D+M'		]
	,
	'sub': [
		'@SP'		,
		'AM=M-1'	,
		'D=M'		,
		'A=A-1'		,
		'M=M-D'		]
	,
	'neg': [
		'@SP'		,
		'A=M-1'		,
		'M=-M'		]
	,
	'eq': [
		'@SP'		,
		'AM=M-1'	,
		'D=M'		,
		'@SP'		,
		'A=M-1'		,
		'D=M-D'		,
		'@{0}'		,
		'D;JEQ'		,
		'@0'		,
		'D=!A'		,
		'@SP'		,
		'A=M-1'		,
		'M=!D'		]
	,
	'gt': [
		'@SP'		,
		'AM=M-1'	,
		'D=M'		,
		'@SP'		,
		'A=M-1'		,
		'D=D-M'		,
		'@32767'	,
		'A=!A'		,
		'D=D&A'		,
		'@{0}'		,
		'D;JEQ'		,
		'@0'		,
		'D=!A'		,
		'@SP'		,
		'A=M-1'		,
		'M=D'		]
	,
	'lt': [
		'@SP'		,
		'AM=M-1'	,
		'D=M'		,
		'@SP'		,
		'A=M-1'		,
		'D=M-D'		,
		'@32767'	,
		'A=!A'		,
		'D=D&A'		,
		'@{0}'		,
		'D;JEQ'		,
		'@0'		,
		'D=!A'		,
		'@SP'		,
		'A=M-1'		,
		'M=D'		]
	,
	'and': [
		'@SP'		,
		'AM=M-1'	,
		'D=M'		,
		'@SP'		,
		'A=M-1'		,
		'M=D&M'		]
	,
	'or': [
		'@SP'		,
		'AM=M-1'	,
		'D=M'		,
		'@SP'		,
		'A=M-1'		,
		'M=D|M'		]
	,
	'not': [
		'@SP'		,
		'A=M-1'		,
		'M=!M'		]
	,
}
		
segment = {
	'local': '@LCL'		,
	'argument': '@ARG'	,
	'this': '@THIS'		,
	'that':	'@THAT'		,
}
	
class C_Base():
	def __init__(self, filename, id, arg1=None, arg2=None):
		self.filename = filename
		self.id = id
		self.arg1 = arg1
		self.arg2 = arg2
		self.info = '{} {} {}'.format(id,arg1,arg2)
		
class C_Arithmetic(C_Base):
	def getassembly(self, currentline):
		#r = ['//'+self.info]
		r,i = [],currentline
		
		for code in commands_arithmetic[self.id]:
			i+=1
			r.append(code.format(i+3))
			
		return r
	
	@property
	def linecount(self):
		return len(commands_arithmetic[self.id])
	
class C_Push(C_Base):
	def getassembly(self, currentline):
		#r = ['//'+self.info]
		r = []
		
		if self.arg1 == 'static':
			r.extend([
				'@'+self.filename+'.'+self.arg2,
				'D=M'
			])
		else:
			r.extend([
				'@'+self.arg2	,
				'D=A'			]
			)
		
			if self.arg1 == 'temp':
				r.extend([
					'@5'			,
					'A=A+D'			,
					'D=M'			]
				)
			elif self.arg1 == 'pointer':
				r.extend([
					'@3'			,
					'A=A+D'			,
					'D=M'			]
				)
			elif self.arg1 != 'constant':
				r.extend([
					segment[self.arg1]	,
					'A=M+D'				,
					'D=M'				]
				)
		
		r.extend([
			'@SP'		,
			'M=M+1'		,
			'A=M-1'		,
			'M=D'		]
		)
			
		return r
		
	@property
	def linecount(self):
		if self.arg1 == 'static' or self.arg1 == 'constant':
			return 6
		else:
			return 9

class C_Pop(C_Base):
	def getassembly(self, currentline):
		#r = ['//'+self.info]
		r = []
		
		if self.arg1 == 'static':
			r.extend([
				'@SP',
				'AM=M-1',
				'D=M',
				'@'+self.filename+'.'+self.arg2,
				'M=D',
			])
			
		else:
			r.extend([
				'@'+self.arg2		,
				'D=A'				]
			)
			
			if self.arg1 == 'temp':
				r.extend([
					'@5'	,
					'D=D+A'	]
				)
			elif self.arg1 == 'pointer':
				r.extend([
					'@3'	,
					'D=D+A'	]
				)
			else:
				r.extend([
					segment[self.arg1]	,
					'D=M+D'				]
				)
			
			r.extend([
				'@R13'		,
				'M=D'		,
				'@SP'		,
				'AM=M-1'	,
				'D=M'		,
				'@R13'		,
				'A=M'		,
				'M=D'		]
			)
			
		return r
		
	@property
	def linecount(self):
		if self.arg1 == 'static':
			return 5
		else:
			return 12
		

class C_Label(C_Base):
	def getassembly(self, currentline):
		return ['(' + self.arg1 + ')']
		
	@property
	def linecount(self):
		return 0
	
class C_Goto(C_Base):
	def getassembly(self, currentline):
		return [
			'@'+self.arg1,
			'0;JMP',
		]
	
	@property
	def linecount(self):
		return 2

class C_If(C_Base):
	def getassembly(self, currentline):
		return [
			'@SP',
			'AM=M-1',
			'D=M',
			'@'+self.arg1,
			'D;JNE',
		]
		
	@property
	def linecount(self):
		return 5
	
class C_Function(C_Base):
	def getassembly(self, currentline):
		r = ['('+self.arg1+')']
	
		c = int(self.arg2)
		for i in range(c):
			r.extend([
				'@SP',
				'M=M+1',
				'A=M-1',
				'M=0',
			])
			
		return r
		
	@property
	def linecount(self):
		c = (4 * int(self.arg2))
		return c 
	
class C_Return(C_Base):

	def getassembly(self, currentline):
		return [
			'@LCL',
			'D=M',
			'@R13',
			'M=D',
			
			'@5',
			'A=D-A',
			'D=M',
			'@R14',
			'M=D',
			
			'@SP',
			'AM=M-1',
			'D=M',
			'@ARG',
			'A=M',
			'M=D',
			
			'D=A',
			'@SP',
			'M=D+1',
			
			'@R13',
			'AM=M-1',
			'D=M',
			'@THAT',
			'M=D',
			
			'@R13',
			'AM=M-1',
			'D=M',
			'@THIS',
			'M=D',
			
			'@R13',
			'AM=M-1',
			'D=M',
			'@ARG',
			'M=D',
			
			'@R13',
			'AM=M-1',
			'D=M',
			'@LCL',
			'M=D',
			
			'@R14',
			'A=M',
			'0;JMP',
		]
		
	@property
	def linecount(self):
		return 41
	
class C_Call(C_Base):
	
	def getassembly(self, currentline):
		retlabel = 'ret-'+str(currentline)+'-'+self.filename+'.'+self.arg1
		r = [
			'@'+retlabel,
			'D=A',
			'@SP',
			'M=M+1',
			'A=M-1',
			'M=D',
			
			'@LCL',
			'D=M',
			'@SP',
			'M=M+1',
			'A=M-1',
			'M=D',
			
			'@ARG',
			'D=M',
			'@SP',
			'M=M+1',
			'A=M-1',
			'M=D',
			
			'@THIS',
			'D=M',
			'@SP',
			'M=M+1',
			'A=M-1',
			'M=D',
			
			'@THAT',
			'D=M',
			'@SP',
			'M=M+1',
			'A=M-1',
			'M=D',
			
			'@SP',
			'D=M',
			'@'+self.arg2,
			'D=D-A',
			'@5',
			'D=D-A',
			'@ARG',
			'M=D',
			'@SP',
			'D=M',
			'@LCL',
			'M=D',
			'@'+self.arg1,
			'0;JMP',
			'('+retlabel+')'
		]
		
		return r
		
	@property
	def linecount(self):
		return 44
		
		
def tokenize(line):
	r = line.strip('\n').partition('//')[0].split(None,2)
	if r:
		if len(r) > 2:
			return True, r[0], r[1], r[2]
		elif len(r) > 1:
			return True, r[0], r[1], None
		elif len(r) > 0:
			return True, r[0], None, None
	return False, None, None, None
		
def parse(files,filename,filenames,init):
	r = []

	if init:
		r.append(C_Call(filename,'call','Sys.init','0'))
	
	for line in fileinput.input(files):
		ok, id, arg1, arg2 = tokenize(line)
		n = fileinput.filename().rpartition('\\')[2].rstrip('.vm')
		if ok:
			if id in commands_arithmetic:
				r.append(C_Arithmetic(n,id,arg1,arg2))
			elif id == 'push':
				r.append(C_Push(n,id,arg1,arg2))
			elif id == 'pop':
				r.append(C_Pop(n,id,arg1,arg2))
			elif id == 'label':
				r.append(C_Label(n,id,arg1,arg2))
			elif id == 'goto':
				r.append(C_Goto(n,id,arg1,arg2))
			elif id == 'if-goto':
				r.append(C_If(n,id,arg1,arg2))
			elif id == 'call':
				r.append(C_Call(n,id,arg1,arg2))
			elif id == 'return':
				r.append(C_Return(n,id,arg1,arg2))
			elif id == 'function':
				r.append(C_Function(n,id,arg1,arg2))
			else:
				error('invalid id: ' + id)
			
	return r
	
command_init = [
	'@256',
	'D=A',
	'@SP',
	'M=D',
]
	
def code(parsed,init):
	coded, i = [], 0
	
	if init:
		coded.extend(command_init)
		i+= len(command_init)
	
	for command in parsed:
		coded.extend(command.getassembly(i))
		i += command.linecount

	return coded
			

if __name__ == "__main__":
	#get file/s
	filename = input('File/Folder name:')
	path = sys.path[0] + '\\' + filename
	init = False
	filenames = []
	if os.path.isdir(path):
		writepath = path + '\\' + filename + '.asm'
		files = []
		for file in os.listdir(path):
			if file.endswith('.vm'):
				files.append(path+'\\'+file)
				filenames.append(file[:-3])
			if file.startswith('Sys'):
				init = True
	elif os.path.isfile(path + '.vm'):
		writepath = path + '.asm'
		files = (path + '.vm')
		filenames.append(filename)
	else:
		error('File not found')
			
	parsed = parse(files,filename,filenames,init)
	coded = code(parsed,init)
	
	#combine strings
	combined = ''
	for i in range(len(coded)):
		#print(i,coded[i])
		combined = combined + coded[i] + '\n'
	
	#open new file
	file = open(writepath, 'w')
	file.write(combined)