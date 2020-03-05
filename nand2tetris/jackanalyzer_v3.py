import sys, io, string, os

symbols = "{}()[].,;+-*/&|<>=~"

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

keywords = ['class', 'constructor', 'function', 'method',
	'field', 'static', 'var', 'int', 'char', 'boolean', 'void',
	'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else',
	'while', 'return', ]

grammar = """
	classDec --> class className { classVarDecSegment subroutineDecSegment }
	name 1.value, variables 3.variables, subroutines 4.subroutines
	classVarDecSegment --> classVarDec classVarDecSegment
	variables list 0.variables 1.variables
	classVarDecSegment --> E
	variables list
	classVarDec --> classVarDec_Scope type varName classVarDec_Tail ;
	3.kind 0.value, 3.type 1.value, kind 0.value, type 1.value, varname 2.value, variables list self 3.variables
	classVarDec_Scope --> static
	value 0.value
	classVarDec_Scope --> field
	value 0.value
	classVarDec_Tail --> , varName classVarDec_Tail
	2.kind kind, 2.type type, varname 1.value, variables list self 2.variables
	classVarDec_Tail --> E
	variables list
	type --> int
	value 0.value
	type --> char
	value 0.value
	type --> boolean
	value 0.value
	type --> className
	value 0.value
	subroutineDecSegment --> subroutineDec subroutineDecSegment
	subroutines list 0.self 1.subroutines
	subroutineDecSegment --> E
	subroutines list
	subroutineDec --> subroutine_Type subroutine_ReturnType subroutineName ( parameterList ) subroutineBody
	type 0.value, returntype 1.value, subroutinename 2.value, parameters 4.parameters, variables 6.variables, statements 6.statements
	subroutine_Type --> constructor
	value 0.value
	subroutine_Type --> function
	value 0.value
	subroutine_Type --> method
	value 0.value
	subroutine_ReturnType --> void
	value 0.value
	subroutine_ReturnType --> type
	value 0.value
	parameterList --> type varName parameterList_Tail
	paramtype 0.value, paramname 1.value, parameters list self 2.parameters
	parameterList --> E
	parameters list
	parameterList_Tail --> , type varName parameterList_Tail
	paramtype 1.value, paramname 2.value, parameters list self 3.parameters
	parameterList_Tail --> E
	parameters list
	subroutineBody --> { varDecSegment statements }
	variables 1.variables, statements 2.statements
	varDecSegment --> varDec varDecSegment
	variables list 0.variables 1.variables
	varDecSegment --> E
	variables list
	varDec --> var type varName varDec_Tail ;
	3.kind 0.value, 3.type 1.value, kind 0.value, type 1.value, varname 2.value, variables list self 3.variables
	varDec_Tail --> , varName varDec_Tail
	2.kind kind, 2.type type, varname 1.value, variables list self 2.variables
	varDec_Tail --> E
	variables list
	className --> identifier
	value 0.value
	subroutineName --> identifier
	value 0.value
	varName --> identifier
	value 0.value
	statements --> statement statements_tail
	statements list 0.self 1.statements
	statements --> E
	statements list
	statements_tail --> statement statements_tail
	statements list 0.self 1.statements
	statements_tail --> E
	statements list
	statement --> letStatement
	kind 0.kind, varname 0.varname, offset 0.offset, expr 0.expr
	statement --> ifStatement
	kind 0.kind, condition 0.condition, body 0.body, tail list 0.tail
	statement --> whileStatement
	kind 0.kind, condition 0.condition, body 0.body
	statement --> doStatement
	kind 0.kind, subroutine 0.subroutine
	statement --> returnStatement
	kind 0.kind, expr 0.expr
	letStatement --> let varName arrayAccess = expression ;
	kind 0.value, varname 1.value, offset 2.value, expr 4.self
	arrayAccess --> [ expression ]
	value 1.self
	arrayAccess --> E
	value 0
	ifStatement --> if ( expression ) { statements } ifStatement_Tail
	kind 0.value, condition 2.self, body 5.statements, tail list 7.statements
	ifStatement_Tail --> else { statements }
	statements list 2.statements
	ifStatement_Tail --> E
	statements list
	whileStatement --> while ( expression ) { statements }
	kind 0.value, condition 2.self, body 5.statements
	doStatement --> do subroutineCall ;
	kind 0.value, subroutine 1.value, args list 1.args
	returnStatement --> return returnExpression ;
	kind 0.value, expr 1.expr
	returnExpression --> expression
	expr 0.self
	returnExpression --> E
	expr none
	expression --> term expression_Tail
	term1 0.value, op 1.op, term2 1.value
	expression_Tail --> op term
	op 0.value, value 1.value
	expression_Tail --> E
	op none, value none
	term --> integerConstant
	value 0.value
	term --> stringConstant
	value 0.value
	term --> keywordConstant
	value 0.value
	term --> varName arrayAccess
	value 0.value, offset 1.value
	term --> subroutineCall
	value 0.value, args list 0.exprlist
	term --> ( expression )
	value 1.self
	term --> unaryOp term
	uop 0.value, value 1.value
	subroutineCall --> subroutineName ( expressionList )
	value 0.value, args list 2.exprlist
	subroutineCall --> subroutineCall_Nonlocal . subroutineName ( expressionList )
	value ref 0.value 2.value, args list 4.exprlist
	subroutineCall_Nonlocal --> className
	value 0.value
	subroutineCall_Nonlocal --> varName
	value 0.value
	expressionList --> expression expressionList_Tail
	exprlist list 0.self 1.exprlist
	expressionList --> E
	exprlist list
	expressionList_Tail --> , expression expressionList_Tail
	exprlist list 1.self 2.exprlist
	expressionList_Tail --> E
	exprlist list
	op --> +
	value 0.value
	op --> -
	value 0.value
	op --> *
	value 0.value
	op --> /
	value 0.value
	op --> &
	value 0.value
	op --> |
	value 0.value
	op --> <
	value 0.value
	op --> >
	value 0.value
	op --> =
	value 0.value
	unaryOp --> -
	value 0.value
	unaryOp --> ~
	value 0.value
	keywordConstant --> true
	value 0.value
	keywordConstant --> false
	value 0.value
	keywordConstant --> null
	value 0.value
	keywordConstant --> this
	value 0.value
"""


class Element():
	indent = '\t'
	ignore = ignore
	replace = replace

	def do_actions(self):
		r = True
		if hasattr(self, 'actionlist'):
			if self.actionlist:
				for action in self.actionlist:
					try:
						action(self)
					except KeyError as e:
						print(self.name, e)
						r = False
					except IndexError as e:
						print(self.name, e)
						r = False
					except AttributeError as e:
						print(self.name, e)
						r = False
		if hasattr(self, 'children'):
			for child in self.children:
				if not child.do_actions():
					r = False
		return r

class Node(Element):
	subscope_key = ['classDec', 'function', 'method', 'constructor']

	def __init__(self, name, scope = None, parent = None):
		self.name = name
		self.children = []
		self.scope = scope
		self.parent = parent
		self.self = self

	def get_attribute(self, id):
		index, sep, attributename = id.rpartition('.')
		if index:
			return getattr(self.children[int(index)], attributename)
		elif attributename == '0':
			return 0
		elif attributename == 'none':
			return None
		else:
			return getattr(self, attributename)

	def get_attribute_list(self, ids):
		l = []
		for id in ids:
			a = self.get_attribute(id)
			if type(a) == list:
				l.extend(a)
			else:
				l.append(a)
		return l

	def set_attribute(self, id, value):
		index, sep, attributename = id.rpartition('.')
		if index:
			setattr(self.children[int(index)], attributename, value)
		else:
			setattr(self, attributename, value)

	def add_node(self, name):
		childscope = self.scope
		if name in self.subscope_key:
			childscope = self.scope.add_subscope()
		child = Node(name, childscope, self)
		self.children.append(child)

		return child

	def add_leaf(self, name, token):
		leaf = Leaf(name, token)
		leaf.parent = self
		self.children.append(leaf)
		if self.name == 'subroutineName':
			self.scope.name = token
		elif self.name == 'varName':
			self.scope

		return leaf

	def __repr__(self, nestlevel=0):
		if self.name in self.ignore:
			s = '\n'.join(child.__repr__(nestlevel) for child in self.children)
			return s
		else:
			s = '\n'.join(child.__repr__(nestlevel+1) for child in self.children)
			return "{0}<{1}>\n{2}\n{0}</{1}>".format(self.indent*nestlevel, self.name, s)

class Leaf(Element):
	def __init__(self, name, token):
		self.name = name
		self.token = token

	@property
	def value(self):
		return self.token

	def __repr__(self, nestlevel=0):
		return "{0}<{1}> {2} </{1}>".format(self.indent*nestlevel, self.name, self.token)

class State(dict):
	def __missing__(self, key):
		if type(key) == str and len(key) == 1:
			for k,v in self.items():
				if type(k) == str and key in k:
					return v
		if key:
			return self[0]

class Scanner():
	symbols = symbols

	def __init__(self):
		self.NEXT_STATE = {
			'STATE_EMPTY': State({
					string.whitespace: 'STATE_EMPTY',
					'/': 'STATE_FWDSLASH',
					'"': 'STATE_STRING',
					self.symbols: 'STATE_SYMBOL',
					0: 'STATE_DEFAULT',
				}),
			'STATE_DEFAULT': State({
					string.whitespace: 'STATE_EMPTY',
					'/': 'STATE_FWDSLASH',
					'"': 'STATE_STRING',
					self.symbols: 'STATE_SYMBOL',
					0: 'STATE_DEFAULT',
				}),
			'STATE_SYMBOL': State({
					string.whitespace: 'STATE_EMPTY',
					'/': 'STATE_FWDSLASH',
					'"': 'STATE_STRING',
					self.symbols: 'STATE_SYMBOL',
					0: 'STATE_DEFAULT',
				}),
			'STATE_FWDSLASH': State({
					string.whitespace: 'STATE_EMPTY',
					'/': 'STATE_COMMENTSINGLE',
					'*': 'STATE_COMMENTMULTI',
					self.symbols: 'STATE_SYMBOL',
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
					self.symbols: 'STATE_SYMBOL',
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
			'STATE_DEFAULT': State({string.whitespace: True, '"': True, self.symbols: True, 0: False}),
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
			state, token, char = 'STATE_EMPTY', "", file.read(1)
			index = 0
			while char:
				if self.CLEARTOKEN[state][char]:
					token = ""
				elif self.ADDTOKEN[state][char]:
					yield token
					token = ""
				token += char
				state = self.NEXT_STATE[state][char]
				index += 1
				char = file.read(1)

def addtoset(A, B):
	changed = False
	for e in B:
		if e not in A:
			A.append(e)
			changed = True
	return changed

class Symbol():
	def __init__(self, name, type, kind, index):
		self.name = name
		self.type, self.kind = type, kind
		self.index = index

class Scope():
	list = []

	def __init__(self, parent=None):
		self.name = "Unnamed"
		self.parent = parent
		self.symbols = {}
		self.kindcounts = {}
		self.subscopes = []

		self.list.append(self)

	def add_subscope(self):
		s = Scope(self)
		self.subscopes.append(s)
		return s

	def get_symbol(self, symbol):
		if symbol in self.symbols:
			return self.symbols[symbol]
		else:
			return self.parent.get_symbol(symbol)

	def add_symbol(self, name, type, kind):
		if kind in self.kindcounts:
			self.kindcounts[kind] += 1
		else:
			self.kindcounts[kind] = 1
		index = self.kindcounts[kind]
		s = Symbol(name, type, kind, index)
		self.symbols[name] = s
		return s

def build_productions(grammar):
	productions, actionlists = {}, {}
	a = False
	lines = grammar.split('\n')
	for i in range(len(lines)):
		if not a:
			lhs, sep, rhs = lines[i].partition('-->')
			lhs, rhs = lhs.strip(), rhs.strip()
			if lhs and rhs:
				actions = lines[i+1].split(',')
				if lhs not in productions:
					productions[lhs] = []
					actionlists[lhs] = []
				productions[lhs].append(rhs)
				actionlists[lhs].append(build_actionlist(actions))
				a = True
		else:
			a = False
		#actionlists[lhs].append(build_actionlist(actions))

	return productions, actionlists


def build_actionlist(actions):
	actionlist = []
	for action in actions:
		args = [s.strip() for s in action.split()]
		if len(args) > 1:
			if args[1] == 'list':
				if len(args) > 2:
					actionlist.append(lambda x: x.set_attribute(args[0], x.get_attribute_list(args[2:])))
				else:
					actionlist.append(lambda x: x.set_attribute(args[0], []))
			else: #direct set
				actionlist.append(lambda x: x.set_attribute(args[0], x.get_attribute(args[1])))

	return actionlist

class Parser():
	symbols = symbols
	keywords = keywords
	grammar = grammar
	ignore = ignore
	replace = replace
	(productions, actionlists) = build_productions(grammar)

	def __init__(self):
		self.idx = 0
		self.nestlevel = 0
		self.out = ""
		self.build_sets()
		self.symboltable = {'global':Scope('global')}
		self.current_scope = self.symboltable['global']
		self.tree = Node('program', self.current_scope)
		self.classes = []

	def set_tokens(self, tokens):
		self.nestlevel = 0
		self.tokens = tokens
		self.count = len(tokens)
		self.idx = 0
		self.current_scope = self.symboltable['global']
		self.current_node = self.tree

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
							changed = addtoset(self.FOLLOW[e[i]], self.first_multi(e[i+1:])) or changed
						for i in range(len(e)):
							if self.eps_multi(e[i+1:]) or i == len(e)-1:
								changed = addtoset(self.FOLLOW[e[i]], self.FOLLOW[lhs]) or changed


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


	def predict(self, name):
		for i, predict_set in enumerate(self.PREDICT[name]):
			if self.isinset(self.tokens[self.idx], predict_set):
				if name == 'subroutineCall':
					if self.tokens[self.idx+1] == '(':
						if self.productions[name][i] == "subroutineName ( expressionList )":
							return self.productions[name][i], self.actionlists[name][i]
					elif self.tokens[self.idx+1] == '.':
						if self.productions[name][i] == "subroutineCall_Nonlocal . subroutineName ( expressionList )":
							return self.productions[name][i], self.actionlists[name][i]
				elif name == 'subroutineCall_Nonlocal':
					if self.productions[name][i] == 'varName':
						return self.productions[name][i], self.actionlists[name][i]
				elif name == 'term' and 'identifier' in predict_set:
					if self.tokens[self.idx+1] in "(.":
						if self.productions[name][i] == 'subroutineCall':
							return self.productions[name][i], self.actionlists[name][i]
					else:
						if self.productions[name][i] == "varName arrayAccess":
							return self.productions[name][i], self.actionlists[name][i]
				else:
					return self.productions[name][i], self.actionlists[name][i]

	def parse(self, name, parent="None"):
		#print("PARSE: {} from {}".format(name,parent))
		#print(self.tokens[self.idx], self.tokens[self.idx+1] if self.idx < self.count-1 else "")
		if name in self.productions:
			p = self.predict(name)
			if not p:
				if self.EPS[name]:
					#print("\tGot it!")
					return True
				else:
					return False
			production, actionlist = p[0], p[1]

			self.nest_down(name)
			self.current_node.actionlist = actionlist
			self.current_node.do_actions()
			for element in production.split():
				if not self.parse(element, name):
					return False
				self.current_node.do_actions()
			self.nest_up()

		else:
			return self.match(name)

		return True

	def nest_down(self, name):
		self.current_node = self.current_node.add_node(name)

	def nest_up(self):
		self.current_node = self.current_node.parent

	def match(self, name):
		#print("MATCH: {}".format(name))
		if name in self.keywords:
			if self.tokens[self.idx] == name:
				self.current_node.add_leaf('keyword', self.tokens[self.idx])
				self.idx = self.idx + 1
				return True
			else:
				#raise SyntaxError("Got {}, expected {}".format(self.tokens[self.idx], name))
				return False
		elif name in self.symbols:
			if self.tokens[self.idx] == name:
				self.current_node.add_leaf('symbol', self.tokens[self.idx])
				self.idx = self.idx + 1
				return True
			else:
				#raise SyntaxError("Got {}, expected {}".format(self.tokens[self.idx], name))
				return False
		elif name == "integerConstant":
			if self.tokens[self.idx].isdigit():
				self.current_node.add_leaf(name, self.tokens[self.idx])
				self.idx = self.idx + 1
				return True
			else:
				#raise SyntaxError("Invalid integerConstant {}".format(self.tokens[self.idx]))
				return False
		elif name == "stringConstant":
			if self.tokens[self.idx].startswith('\"') and self.tokens[self.idx].endswith('\"'):
				self.current_node.add_leaf(name, self.tokens[self.idx].strip('"'))
				self.idx = self.idx + 1
				return True
		elif name == "identifier":
			if self.tokens[self.idx].isidentifier():
				self.current_node.add_leaf(name, self.tokens[self.idx])
				self.idx = self.idx + 1
				return True
			else:
				#raise SyntaxError("Invalid identifier {}".format(self.tokens[self.idx]))
				return False

	def build_symbols ():
		for class in self.tree.children:
			self.symboltable

	def repr_tree(self, node = None, nestlevel = 0):
		if not node:
			node = self.tree
		if type(node) == Leaf:
			s = "{2}<{0}> {1} </{0}>".format(node.name, node.token, '\t'*nestlevel)
			return s
		else:
			if node.name not in self.ignore:
				s = []
				for child in node.children:
					s += self.repr_tree(child,nestlevel+1)
				return "{2}<{0}>\n{1}\n</{0}>".format(node.name, ''.join(s), '\t'*nestlevel)
			else:
				print("TEST")
				s = []
				for child in node.children:
					s += self.repr_tree(child,nestlevel)
				return ','.join(s)

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
		print("File/Folder not found")
		exit()

	return paths, filename


def print_predictinfo(p):
	for k,v in p.PREDICT.items():
		pass
		#print("{}\n\tPREDICT:\n\t\t{}\n\tSECOND:\n\t\t{}".format(k,v,p.SECOND[k]))
	for k,v in p.PREDICT.items():
		for i in range(len(v)-1):
			for e in v[i]:
				for j in range(i+1,len(v)):
					if e in v[j]:
						print("{}\n\t{}\n\t{}".format(k, p.productions[k][i], p.productions[k][j]))

def writefile(lines, filename):
	print("Saving as {}".format(filename))
	path = "{0}\\{1}.xml".format(sys.path[0], filename)
	with open(path, "w") as file:
		file.write(lines)


if __name__ == "__main__":
	try:
		filename = sys.argv[1]
	except IndexError:
		filename = input("File/Folder name:")
	(filepaths, filename) = get_filepaths(filename)

	out = []

	s = Scanner()
	parser = Parser()

	for filepath in filepaths:
		tokens = [token for token in s.readfile(filepath)]
		parser.set_tokens(tokens)
		#print(tokens)
		if parser.parse('classDec'):
			print("Parse successful")
			while True:
				if parser.tree.do_actions():
					break
			print("Decoration successful")
			build_symbols(parser.tree)
			print("Symbol table build successful")
			#print(parser.tree.children[0])
			out.append(repr(parser.tree))
		else:
			print("Parsing failed: {}".format(filepath))
			exit()

	out = "\n".join(out)
	#print(out)
	filename = "out"
	#writefile(out, filename)
