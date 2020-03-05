import sys,os


		
def get_file(name):
	fn = '%s\\%s.jack' % (sys.path[0],name)
	if os.path.isfile(fn):
		return open(fn,"r")
		
	

if __name__ == '__main__':
	#n = input('File/Folder name:')
	n = "Square"
	f = get_file(n)
	
	if not f:
		sys.exit()
		
	comment = False
	
	for line in f:
		pos,length = -1,len(line)-1
		sub = ""
		while pos < length:
			pos+=1
			
			if comment:
				if line[pos-2:pos] == "*/":
					comment = False
				else:
					continue
					
			c = line[pos]
			
			if c == " " or c == "\n":
				if len(sub) > 0:
					print(sub)
				sub = ""
				continue
			
			sub = sub + c
			
			if sub == "//":
				sub = ""
				break
				
			if sub == "/**":
				comment = True
				sub = ""
				continue