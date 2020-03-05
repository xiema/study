import sys, io

"""
	BaseUnit
		- base class for all compilation units
		- variable unitname - used for creating xml file
		- variable unitstring - actual string from the .jack file
		- list of token sequence/s
		- each position in token sequence must be filled by the token string
		- function for looking for all possible next tokens
			(e.g., tokens at position)
		
	ProgramUnit, ClassDec, ClassVarDec, SubroutineDec, ParameterList, SubroutineBody, VarDec,
	
	Statements, Statement, LetStatement, IfStatement, WhileStatement, DoStatement, ReturnStatement,
	Expression, Term, SubroutineCall, ExpressionList
	Atom
	
	Driver
		- if comment, create comment block, scan until end of comment block
		- find all possible follow atoms in current compilation unit, use first match
"""

def tokenize(file):
	tokens = []
	comment = False
	for str in file:
		for token in str.split():
			if comment:
				if token == "*/":
					comment = False
			else:
				if token == "//":
					break
				elif token == "/**":
					comment = True
				else:
					i = 0
					for j in range(0,len(token)):
						if token[j] == "(":
							if i < j:
								tokens.append(token[i,j-1])
							tokens.append(token[j])
							i = j+1
						elif token[j] == ")":
	return tokens
	
def parse(tokens):
	pass

if __name__ == "__main__":
	filename = input("File/Folder name:")
	path = "{0}\\{1}.jack".format(sys.path[0], filename)
	print(path)
	file = open(path, "r")
	
	tokens = tokenize(file)
	print(tokens)
	