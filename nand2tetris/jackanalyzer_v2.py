import sys, io, string, os

_builtin_symbols = "{}()[].,;+-*/&|<>=~"

class SyntaxError(Exception):
	pass

class State(dict):
	def __missing__(self, key):
		if type(key) == str:
			for k,v in self.items():
				if type(k) == str and key in k:
					return v
		return self[0]

class Scanner():
	def __init__(self):
		self.NEXT_STATE = {
			'STATE_EMPTY': State({
					string.whitespace: 'STATE_EMPTY',
					'/': 'STATE_FWDSLASH',
					'"': 'STATE_STRING',
					_builtin_symbols: 'STATE_SYMBOL',
					0: 'STATE_DEFAULT',
				}),
			'STATE_DEFAULT': State({
					string.whitespace: 'STATE_EMPTY',
					'/': 'STATE_FWDSLASH',
					'"': 'STATE_STRING',
					_builtin_symbols: 'STATE_SYMBOL',
					0: 'STATE_DEFAULT',
				}),
			'STATE_SYMBOL': State({
					string.whitespace: 'STATE_EMPTY',
					'/': 'STATE_FWDSLASH',
					'"': 'STATE_STRING',
					_builtin_symbols: 'STATE_SYMBOL',
					0: 'STATE_DEFAULT',
				}),
			'STATE_FWDSLASH': State({
					string.whitespace: 'STATE_EMPTY',
					'/': 'STATE_COMMENTSINGLE',
					'*': 'STATE_COMMENTMULTI',
					_builtin_symbols: 'STATE_SYMBOL',
					0: 'STATE_DEFAULT',
				}),
			'STATE_COMMENTSINGLE': State({
					'\n': 'STATE_EMPTY',
					0: 'STATE_COMMENTSINGLE',
				}),
			'STATE_COMMENTMULTI': State({
					'*': 'STATE_COMMENTMULTI_AST',
					0: 'STATE_COMMENTMULTI',
				}),
			'STATE_COMMENTMULTI_AST': State({
					'/': 'STATE_EMPTY',
					0: 'STATE_COMMENTMULTI',
				}),
			'STATE_STRING': State({
					'"': 'STATE_STRING_END',
					0: 'STATE_STRING',
				}),
			'STATE_STRING_END': State({
					string.whitespace: 'STATE_EMPTY',
					'/': 'STATE_FWDSLASH',
					'"': 'STATE_STRING',
					_builtin_symbols: 'STATE_SYMBOL',
					0: 'STATE_DEFAULT',
				}),
		}

		self.CLEARTOKEN = {
			'STATE_EMPTY': State({0: True}),
			'STATE_DEFAULT': State({0: False}),
			'STATE_SYMBOL': State({0: False}),
			'STATE_FWDSLASH': State({'/': True, '*': True, 0: False}),
			'STATE_COMMENTSINGLE': State({0: True}),
			'STATE_COMMENTMULTI': State({0: True}),
			'STATE_COMMENTMULTI_AST': State({0: True}),
			'STATE_STRING': State({0: False}),
			'STATE_STRING_END': State({0: False}),
		}

		self.ADDTOKEN = {
			'STATE_EMPTY': State({0: False}),
			'STATE_DEFAULT': State({string.whitespace: True, '"': True, _builtin_symbols: True, 0: False}),
			'STATE_SYMBOL': State({0: True}),
			'STATE_FWDSLASH': State({'/': False, '*': False, 0: True}),
			'STATE_COMMENTSINGLE': State({0: False}),
			'STATE_COMMENTMULTI': State({0: False}),
			'STATE_COMMENTMULTI_AST': State({0: False}),
			'STATE_STRING': State({0: False}),
			'STATE_STRING_END': State({0: True}),
		}

	def readfile(self, filepath):
		with open(filepath, 'r') as file:
			state, token, char = 'STATE_EMPTY', "", ' '
			index = 0
			while char:
				char = file.read(1)
				if self.CLEARTOKEN[state][char]:
					token = ""
				elif self.ADDTOKEN[state][char]:
					yield token
					token = ""
				token += char
				state = self.NEXT_STATE[state][char]
				index += 1


def scanner(filepath):
	with open(filepath, 'r') as file:
		tokens = []
		token = ""
		state = 0

		token = file.read(1)
		while token:
			c = file.read(1)
			if state == 0:
				if token in _builtin_symbols:
					if token == "/" and c == "/":
						state = 1
						token = file.read(1)
					elif token == "/" and c == "*":
						state = 2
						token = file.read(1)
					else:
						tokens.append(token)
						token = c
				elif token == '"':
					state = 3
					token += c
				elif token in string.whitespace:
					token = c
				else:
					if c in string.whitespace or c in _builtin_symbols or c == "":
						tokens.append(token)
						token = c
					else:
						token += c
			elif state == 1:
				if token == '\n':
					state = 0
				token = c
			elif state == 2:
				if token == "*" and c == "/":
					state = 0
					token = file.read(1)
				else:
					token = c
			elif state == 3:
				if c == '"':
					state = 0
					token += c
					tokens.append(token)
					token = file.read(1)
				else:
					token += c

		return tokens

def addtoset(A, B):
	changed = False
	for e in B:
		if e not in A:
			A.append(e)
			changed = True
	return changed

class Parser():
	symbols = "{}()[].,;+-*/&|<>=~"
	keywords = ['class', 'constructor', 'function', 'method',
		'field', 'static', 'var', 'int', 'char', 'boolean', 'void',
		'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else',
		'while', 'return', ]
	productions = {
		'classDec': ["class className { classVarDecSegment subroutineDecSegment }"],
		'classVarDecSegment': ["classVarDec classVarDecSegment", 'E'],
		'classVarDec': ["classVarDec_Scope type varName classVarDec_Tail ;"],
		'classVarDec_Scope': ['static', 'field'],
		'classVarDec_Tail': [", varName classVarDec_Tail", 'E'],
		'type': ['int', 'char', 'boolean', 'className'],
		'subroutineDecSegment': ["subroutineDec subroutineDecSegment", 'E'],
		'subroutineDec': ["subroutine_Type subroutine_ReturnType subroutineName ( parameterList ) subroutineBody"],
		'subroutine_Type': ['constructor', 'function', 'method'],
		'subroutine_ReturnType': ['void', 'type'],
		'parameterList': ["type varName parameterList_Tail", 'E'],
		'parameterList_Tail': [", type varName parameterList_Tail", 'E'],
		'subroutineBody': ["{ varDecSegment statements }"],
		'varDecSegment': ["varDec varDecSegment", 'E'],
		'varDec': ["var type varName varDec_Tail ;"],
		'varDec_Tail': [", varName varDec_Tail", 'E'],
		'className': ['identifier'],
		'subroutineName': ['identifier'],
		'varName': ['identifier'],
		'statements': ["statement statements_tail", 'E'],
		'statements_tail': ["statement statements_tail", 'E'],
		'statement': ['letStatement', 'ifStatement', 'whileStatement', 'doStatement', 'returnStatement'],
		'letStatement': ["let varName arrayAccess = expression ;"],
		'arrayAccess': ["[ expression ]", 'E'],
		'ifStatement': ["if ( expression ) { statements } ifStatement_Tail"],
		'ifStatement_Tail': ["else { statements }", 'E'],
		'whileStatement': ["while ( expression ) { statements }"],
		'doStatement': ["do subroutineCall ;"],
		'returnStatement': ["return returnExpression ;"],
		'returnExpression': ['expression', 'E'],
		'expression': ["term expression_Tail"],
		'expression_Tail': ["op term", 'E'],
		'term': ['integerConstant', 'stringConstant', 'keywordConstant', "varName arrayAccess", 'subroutineCall', "( expression )", "unaryOp term"],
		'subroutineCall': ["subroutineName ( expressionList )", "subroutineCall_Nonlocal . subroutineName ( expressionList )"],
		'subroutineCall_Nonlocal': ['className', 'varName'],
		'expressionList': ["expression expressionList_Tail", 'E'],
		'expressionList_Tail': [", expression expressionList_Tail", 'E'],
		'op': ['+', '-', '*', '/', '&', '|', '<', '>', '='],
		'unaryOp': ['-', '~'],
		'keywordConstant': ['true', 'false', 'null', 'this'],
	}

	ignore = [
		'classVarDecSegment', 'classVarDec_Scope', 'classVarDec_Tail', 'subroutineDecSegment',
		'subroutine_Type', 'subroutine_ReturnType',
		'parameterList_Tail',
		'varDecSegment',
		'varDec_Tail',
		'arrayAccess',
		'statement', 'statements_tail', 'ifStatement_Tail',
		'returnExpression',
		'expression_Tail',
		'subroutineCall', 'subroutineCall_Nonlocal',
		'expressionList_Tail',
		'className', 'varName', 'subroutineName', 'type', 'op', 'keywordConstant', 'unaryOp',
		]

	replace = {
		'classDec' : 'class',
		'<' : '&lt;',
		'>' : '&gt;',
		'&' : '&amp;',
	}

	def __init__(self, tokens):
		self.tokens = tokens
		self.idx = 0
		self.count = len(tokens)
		self.nestlevel = 0
		self.out = ""

	def first_multi(self, table):
		t = []
		for e in table:
			t.extend(self.FIRST[e])
			if not self.EPS[e]:
				return t
		return t

	def eps_multi(self, table):
		for e in table:
			if not self.EPS[e]:
				return False
		return True

	def single_multi(self, table):
		b = False
		for e in table:
			if b:
				if not self.EPS[e]:
					return False
			else:
				b = self.SINGLE[e]
		return b

	def predict_multi(self, table):
		t = []
		for e in table:
			if e in self.productions:
				for p in self.PREDICT[e]:
					t.extend(p)
			else:
				t.append(e)
			if not self.EPS[e]:
				return t
		return t

	def build_sets(self):
		self.FIRST, self.FOLLOW, self.PREDICT,self.EPS = {}, {}, {}, {}

		#FIRST
		for symbol in self.symbols:
			self.FIRST[symbol] = [symbol]
			self.EPS[symbol] = False
		for keyword in self.keywords:
			self.FIRST[keyword] = [keyword]
			self.EPS[keyword] = False
		self.FIRST['identifier'], self.EPS['identifier'] = ['identifier'], False
		self.FIRST['integerConstant'], self.EPS['integerConstant'] = ['integerConstant'], False
		self.FIRST['stringConstant'], self.EPS['stringConstant'] = ['stringConstant'], False
		for lhs, rhs_list in self.productions.items():
			self.FIRST[lhs] = []
			self.EPS[lhs] = True if 'E' in rhs_list else False

		changed = True
		while changed:
			changed = False
			for lhs, rhs_list in self.productions.items():
				for rhs in rhs_list:
					if rhs != 'E':
						alleps = True
						for e in rhs.split():
							changed = addtoset(self.FIRST[lhs], self.FIRST[e])
							if not self.EPS[e]:
								alleps = False
								break
						if alleps:
							self.EPS[lhs] = True

		#FOLLOW
		for symbol in self.symbols:
			self.FOLLOW[symbol] = []
		for keyword in self.keywords:
			self.FOLLOW[keyword] = []
		self.FOLLOW['identifier'], self.FOLLOW['integerConstant'], self.FOLLOW['stringConstant'] = [],[],[]
		for lhs, rhs_list in self.productions.items():
			self.FOLLOW[lhs] = []

		changed = True
		while changed:
			changed = False
			for lhs, rhs_list in self.productions.items():
				for rhs in rhs_list:
					if rhs != 'E':
						e = rhs.split()
						for i in range(len(e)-1):
							changed = changed or addtoset(self.FOLLOW[e[i]], self.first_multi(e[i+1:]))
						for i in range(len(e)):
							if self.eps_multi(e[i+1:]) or i == len(e)-1:
								changed = changed or addtoset(self.FOLLOW[e[i]], self.FOLLOW[lhs])


		#PREDICT
		for lhs, rhs_list in self.productions.items():
			self.PREDICT[lhs] = []
			for i in range(len(rhs_list)):
				if rhs_list[i] != 'E':
					self.PREDICT[lhs].insert(i, [])
					l = rhs_list[i].split()
					addtoset(self.PREDICT[lhs][i], self.first_multi(l))
					if self.eps_multi(l):
						addtoset(self.PREDICT[lhs][i], self.FOLLOW[lhs])


		#PEEK
		self.SINGLE, self.SECOND = {}, {}
		for symbol in self.symbols:
			self.SINGLE[symbol] = True
			self.SECOND[symbol] = []
		for keyword in self.keywords:
			self.SINGLE[keyword] = True
			self.SECOND[keyword] = []
		self.SINGLE['identifier'], self.SECOND['identifier'] = True, []
		self.SINGLE['integerConstant'], self.SECOND['integerConstant'] = True, []
		self.SINGLE['stringConstant'], self.SECOND['stringConstant'] = True, []
		for lhs, rhs_list in self.productions.items():
			self.SINGLE[lhs] = False
			self.SECOND[lhs] = []
			for rhs in rhs_list:
				self.SECOND[lhs].append([])

		changed = True
		while changed:
			changed = False
			for lhs, rhs_list in self.productions.items():
				if not self.SINGLE[lhs]:
					for rhs in rhs_list:
						if rhs != 'E':
							elements = rhs.split()
							if self.single_multi(elements):
								self.SINGLE[lhs], changed = True, True

		changed = True
		while changed:
			changed = False
			for lhs, rhs_list in self.productions.items():
				for idx, rhs in enumerate(rhs_list):
					if rhs != 'E':
						elements = rhs.split()
						for i, e in enumerate(elements):
							cont = True
							if self.single_multi(elements[:i]):
								changed = addtoset(self.SECOND[lhs][idx], self.predict_multi(elements[i:])) or changed
								if self.eps_multi(elements[i:]):
									changed = addtoset(self.SECOND[lhs][idx], ['E']) or changed
								cont = True
							if self.eps_multi(elements[:i]):
								for s in self.SECOND[e]:
									changed = addtoset(self.SECOND[lhs][idx], s) or changed
								cont = True
							if not cont:
								break


	def isinset(self, token, set):
		if token in set:
			return True
		elif ('identifier' in set and token.isidentifier()):
			return True
		elif ('integerConstant' in set and token.isdigit()):
			return True
		elif ('stringConstant' in set) and token.startswith('\"') and token.endswith('\"'):
			return True
		return False


	def parse(self, name, parent="None"):
		if name == 'classDec':
			self.printnonterminal('classDec')
		#print("PARSE: {} from {}".format(name,parent))
		#print(self.tokens[self.idx], self.tokens[self.idx+1] if self.idx < self.count-1 else "")
		if name in self.productions:
			a = -1
			for i, predict_set in enumerate(self.PREDICT[name]):
				if self.isinset(self.tokens[self.idx], predict_set):
					if len(self.productions[name]) == 1:
						a = i
						#print("\tGot it!")
						break
					else:
						s = self.SECOND[name][i]
						#print("\t{}\n\t\t{}\n\t\t{}".format(name, predict_set, s))
						if len(s) == 0 or self.isinset(self.tokens[self.idx+1], s):
							a = i
							#print("\tGot it!")
							break
						elif 'E' in s:
							a = i
			if a < 0:
				if 'E' in self.productions[name]:
					#print("\tGot it!")
					return True
				else:
					return False

			if name not in self.ignore:
				#self.printnonterminal(name)
				self.nestlevel += 1
			for element in self.productions[name][a].split():
				self.printnonterminal(element)
				if not self.parse(element, name):
					return False
				self.printnonterminal_end(element)
			if name not in self.ignore:
				self.nestlevel -= 1
				#self.printnonterminal_end(name)

		else:
			return self.match(name)

		if name == 'classDec':
			self.printnonterminal_end('classDec')

		return True

	def printnonterminal(self, name):
		if name in self.productions and name not in self.ignore:
			if name in self.replace:
				name = self.replace[name]
			s = "{}<{}>".format(self.nestlevel * '\t', name)
			#print(s)
			self.out += s + '\n'

	def printnonterminal_end(self, name):
		if name in self.productions and name not in self.ignore:
			if name in self.replace:
				name = self.replace[name]
			s = "{}</{}>".format(self.nestlevel * '\t', name)
			#print(s)
			self.out += s + '\n'

	def printterminal(self, name):
		t = self.tokens[self.idx]
		if name == 'stringConstant':
			t = t.strip('"')
		elif t in self.replace:
			t = self.replace[t]
		s = "{0}<{1}> {2} </{1}>".format(self.nestlevel * '\t', name, t)
		#print(s)
		self.out += s + '\n'

	def match(self, name):
		#print("MATCH: {}".format(name))
		if name in self.keywords:
			if self.tokens[self.idx] == name:
				self.printterminal('keyword')
				self.idx = self.idx + 1
				return True
			else:
				#raise SyntaxError("Got {}, expected {}".format(self.tokens[self.idx], name))
				return False
		elif name in self.symbols:
			if self.tokens[self.idx] == name:
				self.printterminal('symbol')
				self.idx = self.idx + 1
				return True
			else:
				#raise SyntaxError("Got {}, expected {}".format(self.tokens[self.idx], name))
				return False
		elif name == "integerConstant":
			if self.tokens[self.idx].isdigit():
				self.printterminal(name)
				self.idx = self.idx + 1
				return True
			else:
				#raise SyntaxError("Invalid integerConstant {}".format(self.tokens[self.idx]))
				return False
		elif name == "stringConstant":
			if self.tokens[self.idx].startswith('\"') and self.tokens[self.idx].endswith('\"'):
				self.printterminal(name)
				self.idx = self.idx + 1
				return True
		elif name == "identifier":
			if self.tokens[self.idx].isidentifier():
				self.printterminal(name)
				self.idx = self.idx + 1
				return True
			else:
				#raise SyntaxError("Invalid identifier {}".format(self.tokens[self.idx]))
				return False

def get_filepaths(filename):
	path = "{0}\\{1}".format(sys.path[0], filename)
	paths = []
	if os.path.isdir(path):
		for file in os.listdir(path):
			if file.endswith('.jack'):
				paths.append(path + '\\' + file)
	elif os.path.isfile(path):
		paths.append(path)
		filename = filename.split('.jack')[0]
	else:
		error("File/Folder not found")

	return paths, filename

def print_predictinfo(p):
	for k,v in p.PREDICT.items():
		print("{}\n\tPREDICT:\n\t\t{}\n\tSECOND:\n\t\t{}".format(k,v,p.SECOND[k]))
	for k,v in p.PREDICT.items():
		for i in range(len(v)-1):
			for e in v[i]:
				for j in range(i+1,len(v)):
					if e in v[j]:
						for ee in p.SECOND[k][i]:
							if ee in p.SECOND[k][j]:
								print(i,j,"NOT LR(1)!",e,ee)


if __name__ == "__main__":
	try:
		filename = sys.argv[1]
	except IndexError:
		filename = input("File/Folder name:")
	(filepaths, filename) = get_filepaths(filename)

	out = []

	s = Scanner()
	for filepath in filepaths:
		tokens = [token for token in s.readfile(filepath)]
		print(tokens)

	exit()

	for filepath in filepaths:
		tokens = scanner(filepath)
		#print(tokens)
		parser = Parser(tokens)
		parser.build_sets()
		if parser.parse('classDec'):
			print("Successful!")
			out.append(parser.out)
		else:
			error("Parsing failed: {}".format(filepath))

	out = "\n".join(out)
	#print(out)
	filename = "out"
	print("Saving as {}".format(filename))
	path = "{0}\\{1}.xml".format(sys.path[0], filename)
	file = open(path, "w")
	file.write(out)
