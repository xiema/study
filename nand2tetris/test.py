import sys,os,fileinput

def get_lines(filenames):
	r = []
	for line in fileinput.input(filenames):
		r.append(line)
	return r
	
class Parser():

	def parse(self, lines):
		self.return = []
		self.lines = lines
		while self.lines[0] is not None:
			self.advance()
		return self.return
		
	def advance(self):
		if len(self.tokens) > 0:
			if self.tokens[0] == '
		

if __name__ == '__main__':
	print('JACK SCANNER')
	n = input('File/Folder name:')
	
	p = '%s\\%s' % (sys.path[0],n)
	
	if os.path.isdir(p):
		print(os.curdir)
		os.chdir(p)
		filein = []
		for fn in os.listdir():
			print(fn)
			if fn.endswith('.jack'):
				filein.append(fn)
				
	else:
		fn = n + '.jack'
		if os.path.isfile(fn):
			filein = fn
			
	lines = tokenize(filein)
	parsed = parse(lines)
	for i in range(100):
		print(i,parsed[i])