import sys, io, string, os
from collections import namedtuple,Counter

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
	name 1.value, scope.name name, variables 3.variables, subroutines 4.subroutines
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
	type 0.value, returntype 1.value, subroutinename 2.value, scope.name subroutinename, parameters 4.parameters, variables 6.variables, statements 6.statements
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
	kind 0.kind, condition 0.condition, body list 0.body, tail list 0.tail
	statement --> whileStatement
	kind 0.kind, condition 0.condition, body list 0.body
	statement --> doStatement
	kind 0.kind, subroutine 0.subroutine
	statement --> returnStatement
	kind 0.kind, expr 0.expr
	letStatement --> let varName arrayAccess = expression ;
	kind 0.value, varname 1.value, offset 2.expr, expr 4.self
	arrayAccess --> [ expression ]
	expr 1.self
	arrayAccess --> E
	value 0
	ifStatement --> if ( expression ) { statements } ifStatement_Tail
	kind 0.value, condition 2.self, body list 5.statements, tail list 7.statements
	ifStatement_Tail --> else { statements }
	statements list 2.statements
	ifStatement_Tail --> E
	statements list
	whileStatement --> while ( expression ) { statements }
	kind 0.value, condition 2.self, body list 5.statements
	doStatement --> do subroutineCall ;
	kind 0.value, subroutine 1.self
	returnStatement --> return returnExpression ;
	kind 0.value, expr 1.expr
	returnExpression --> expression
	expr 0.self
	returnExpression --> E
	expr 0
	expression --> term expression_Tail
	terms list 0.self 1.terms, operators list 1.operators
	expression_Tail --> op term expression_Tail
	operators list 0.value 2.operators, terms list 1.self 2.terms
	expression_Tail --> E
	operators list, terms list
	term --> integerConstant
	type *.integer, value 0.value
	term --> stringConstant
	type *.string, value 0.value
	term --> keywordConstant
	type *.keyword, value 0.value
	term --> varName arrayAccess
	type *.variable, varname 0.value, offset 1.expr
	term --> subroutineCall
	type *.subroutine, subroutine 0.self
	term --> ( expression )
	type *.expression, expr 1.self
	term --> unaryOp term
	type *.unaryop, op 0.value, term 1.self
	subroutineCall --> subroutineName ( expressionList )
	subroutinename list 0.value, args list 2.exprlist
	subroutineCall --> subroutineCall_Nonlocal . subroutineName ( expressionList )
	subroutinename list 0.value 2.value, args list 4.exprlist
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


class CodeWriter():

	code_operations = {
		'+' : "add",
		'-' : "sub",
		'*' : "call Math.multiply 2",
		'/' : "call Math.divide 2",
		'&' : "and",
		'|' : "or",
		'<' : "lt",
		'>' : "gt",
		'=' : "eq",
	}
	code_keywords = {
		'true' : "constant 1\n\tneg",
		'false' : "constant 0",
		'null' : "constant 0",
		'this' : "pointer 0",
	}

	def code(self, tree):
		files = []
		self.labelcount = 0

		for c in tree.children:
			self.lines = []
			for sub in c.subroutines:
				sym = c.scope.get_symbol_func(sub.subroutinename)
				self.append('function', sym.name, sym.varcount)
				if sub.type == 'constructor':
					self.append('push', 'constant', c.fieldcount)
					self.append('call', 'Memory.alloc', 1)
					self.append('pop', 'pointer', 0)
				elif sub.type == 'method':
					self.append('push', 'argument', 0)
					self.append('pop', 'pointer', 0)
				for st in sub.statements:
					self.code_statement(st)
			files.append((c.filename, self.lines))

		self.lines,self.labelcount = None,None
		return files

	def code_statement(self, st):
		if st.kind == 'let':
			vsym = st.scope.get_symbol_var(st.varname)
			self.code_expression(st.expr)
			if st.offset:
				self.code_expression(st.offset)
				self.append('push', vsym.kind, vsym.index)
				self.append('add')
				self.append('pop', 'pointer', 1)
				self.append('pop', 'that', 0)
			else:
				self.append('pop', vsym.kind, vsym.index)

		elif st.kind == 'if':
			lab_body = "IF.{}.BODY".format(self.labelcount)
			lab_end = "IF.{}.END".format(self.labelcount)
			self.labelcount+=1
			self.code_expression(st.condition)
			self.append('if-goto', lab_body)
			if st.tail:
				for tst in st.tail:
					self.code_statement(tst)
			self.append('goto', lab_end)
			self.append('label', lab_body)
			if st.body:
				for bst in st.body:
					self.code_statement(bst)
			self.append('label', lab_end)

		elif st.kind == 'while':
			lab_body = "WHILE.{}.BODY".format(self.labelcount)
			lab_cond = "WHILE.{}.COND".format(self.labelcount)
			self.labelcount+=1
			self.append('goto', lab_cond)
			self.append('label', lab_body)
			if st.body:
				for bst in st.body:
					self.code_statement(bst)
			self.append('label', lab_cond)
			self.code_expression(st.condition)
			self.append('if-goto', lab_body)

		elif st.kind == 'do':
			self.code_subroutine_call(st.subroutine)

		elif st.kind == 'return':
			if st.expr:
				self.code_expression(st.expr)
			else:
				self.append('push', 'constant', 0)
			self.append('return')

	def code_subroutine_call(self, sub):
		name = '.'.join(sub.subroutinename)
		fsym = None
		if len(sub.subroutinename) > 1:
			try:
				vsym = sub.scope.get_symbol_var(sub.subroutinename[0])
				name = "{}.{}".format(vsym.type, sub.subroutinename[1])
				fsym = sub.scope.get_symbol_func(name, len(sub.args)+1)
				self.append('push', vsym.kind, vsym.index)
			except SyntaxError:
				fsym = sub.scope.get_symbol_func(name, len(sub.args))
		else:
			fsym = sub.scope.get_symbol_func(name, len(sub.args)+1)
			self.append('push', 'pointer', 0)
		for expr in sub.args:
			self.code_expression(expr)
		self.append('call', fsym.name, fsym.argcount)
		if fsym.returntype == 'void':
			self.append('pop', 'temp', 0)

	def code_expression(self, expr):
		self.code_term(expr.terms[0])
		for i,op in enumerate(expr.operators):
			self.code_term(expr.terms[i+1])
			self.append(self.code_operations[op])

	def code_term(self, term):
		if term.type == 'integer':
			self.append('push', 'constant', term.value)
		elif term.type == 'string':
			self.code_string(term.value)
		elif term.type == 'keyword':
			self.append('push', self.code_keywords[term.value])
		elif term.type == 'variable':
			sym = term.scope.get_symbol_var(term.varname)
			self.append('push', sym.kind, sym.index)
			if term.offset:
				self.code_expression(term.offset)
				self.append('add')
				self.append('pop', 'pointer', 1)
				self.append('push', 'that', 0)
		elif term.type == 'subroutine':
			self.code_subroutine_call(term.subroutine)
		elif term.type == 'expression':
			self.code_expression(term.expr)
		elif term.type == 'unaryop':
			self.code_term(term.term)
			if term.op == '-':
				self.append('neg')
			elif term.op == '~':
				self.append('not')

	def code_string(self, string):
		self.append('push', 'constant', len(string))
		self.append('call', 'String.new', 1)
		for c in string:
			self.append('push', 'constant', ord(c))
			self.append('call', 'String.appendChar', 2)

	def append(self, *args):
		pre = None
		if args[0] == 'function':
			pre = ''
		elif args[0] == 'label':
			pre = ''
		else:
			pre = '\t'
		args = [str(a) for a in args]
		self.lines.append(pre + ' '.join(args))

def do_action(node, args):
	if len(args) > 1:
		if args[1] == 'list':
			if len(args) > 2:
				node.set_attribute(args[0],node.get_attribute_list(args[2:]))
			else:
				node.set_attribute(args[0], [])
		else: #direct set
			node.set_attribute(args[0], node.get_attribute(args[1]))


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
						do_action(self,action)
					except KeyError as e:
						print(self.index, self.name, e)
						r = False
					except IndexError as e:
						print(self.index, self.name, e)
						r = False
					except AttributeError as e:
						print(self.index, self.name, e)
						r = False
		if hasattr(self, 'children'):
			for child in self.children:
				#print(child.name)
				if not child.do_actions():
					r = False
		return r

	def print_attributes(self):
		if hasattr(self, 'actionlist'):
			print(self.name)
			for action in self.actionlist:
				print("\t{} = {}".format(action[0], self.get_attribute(action[0])))

		if hasattr(self, 'children'):
			for child in self.children:
				child.print_attributes()

class Node(Element):
	subscope_key = ['classDec', 'subroutineDec']
	cnt = 0

	def __init__(self, name, scope = None, parent = None, null = False):
		self.name = name
		self.children = []
		self.scope = scope
		self.parent = parent
		self.self = self
		self.index = Node.cnt
		self.null = null
		Node.cnt+=1

	def get_attribute(self, id):
		#print(self.name,id)
		index, sep, attributename = id.rpartition('.')
		if index:
			if index == '*':
				return attributename
			elif self.children[int(index)].null:
				return None
			else:
				return getattr(self.children[int(index)], attributename)
		elif attributename == '0':
			return 0
		elif not self.null:
			return getattr(self, attributename)
		else:
			return None

	def get_attribute_list(self, ids):
		if self.null:
			return []
		l = []
		for id in ids:
			a = self.get_attribute(id)
			if a:
				if type(a) == list:
					l.extend(a)
				else:
					l.append(a)
		return l

	def set_attribute(self, id, value):
		if id == 'scope.name':
			self.scope.name = value
			return
		index, sep, attributename = id.rpartition('.')
		if index:
			setattr(self.children[int(index)], attributename, value)
		else:
			setattr(self, attributename, value)

	def add_node(self, name, null=False):
		childscope = self.scope
		if name in self.subscope_key:
			childscope = self.scope.add_subscope()
		child = Node(name, childscope, self, null=null)
		self.children.append(child)

		return child

	def add_leaf(self, name, token):
		leaf = Leaf(name, token)
		leaf.parent = self
		self.children.append(leaf)

		return leaf

	def get_xml(self, nestlevel=0):
		if self.name in self.ignore:
			s = '\n'.join(child.get_xml(nestlevel) for child in self.children)
			return s
		else:
			s = '\n'.join(child.get_xml(nestlevel+1) for child in self.children)
			return "{0}<{1}>\n{2}\n{0}</{1}>".format(self.indent*nestlevel, self.name, s)

class Leaf(Element):
	def __init__(self, name, token, null=False):
		self.name = name
		self.token = token
		self.self = self
		self.null = null

	@property
	def value(self):
		return self.token

	def get_xml(self, nestlevel=0):
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

SymbolInfo = namedtuple('SymbolInfo', ['name', 'type', 'kind', 'index'])
FunctionInfo = namedtuple('FunctionInfo', ['name','type', 'returntype', 'argcount','varcount'])

class Scope():
	list = []
	globalsymbols = {}
	globalcount = 0

	os_functions = [
		('String.dispose', 'method', 'void', 0, 0),
		('String.setCharAt', 'method', 'void', 1, 0),
		('String.eraseLastChar', 'method', 'void', 0, 0),
		('String.setInt', 'method', 'void', 1, 0),
		('Array.dispose', 'method', 'void', 0, 0),
		('String.dispose', 'method', 'void', 0, 0),
		('Output.moveCursor', 'function', 'void', 2, 0),
		('Output.printChar', 'function', 'void', 1, 0),
		('Output.printString', 'function', 'void', 1, 0),
		('Output.printInt', 'function', 'void', 11, 0),
		('Output.println', 'function', 'void', 0, 0),
		('Output.backSpace', 'function', 'void', 0, 0),
		('Screen.clearScreen', 'function', 'void', 0, 0),
		('Screen.setColor', 'function', 'void', 1, 0),
		('Screen.drawPixel', 'function', 'void', 2, 0),
		('Screen.drawLine', 'function', 'void', 4, 0),
		('Screen.drawRectangle', 'function', 'void', 4, 0),
		('Screen.drawCircle', 'function', 'void', 3, 0),
		('Memory.poke', 'function', 'void', 2, 0),
		('Memory.deAlloc', 'function', 'void', 1, 0),
		('Sys.halt', 'function', 'void', 0, 0),
		('Sys.error', 'function', 'void', 1, 0),
		('Sys.wait', 'function', 'void', 1, 0),

	]

	def __init__(self, parent=None):
		self.name = "Unnamed"
		self.parent = parent
		self.symbols = {}
		self.kindcounts = Counter()
		self.subscopes = []

		self.list.append(self)
		for f in self.os_functions:
			self.globalsymbols[f[0]] = FunctionInfo(*f)


	def add_subscope(self):
		s = Scope(self)
		self.subscopes.append(s)
		return s

	def get_symbol_var(self, symbol):
		if symbol in self.symbols:
			if type(self.symbols[symbol]) == SymbolInfo:
				return self.symbols[symbol]
			raise SyntaxError("Symbol {} is not a variable but used like a variable".format(symbol))
		elif self.parent:
			return self.parent.get_symbol_var(symbol)
		raise SyntaxError("Symbol {} is not visible in this scope".format(symbol))

	def get_symbol_func(self, symbol, argcount=None):
		if symbol in self.symbols:
			if type(self.symbols[symbol]) == FunctionInfo:
				if argcount and argcount != self.symbols[symbol].argcount:
					raise SyntaxError("Function {} takes {} arguments but passed {}".format(self.symbols[symbol].name, self.symbols[symbol].argcount, argcount))
				return self.symbols[symbol]
			raise SyntaxError("Symbol {} is not a function but used like a function".format(symbol))
		elif self.parent:
			return self.parent.get_symbol_func(symbol, argcount)
		else:
			self.globalsymbols[symbol] = FunctionInfo(symbol, 'function', 'unknown', argcount, 0)
			return self.globalsymbols[symbol]

	def check_symbol(self, name, opt):
		if opt:
			if name in self.globalsymbols:
				raise SyntaxError("Symbol \'{}\' has already been declared in global scope".format(name))
		else:
			if name in self.symbols:
				raise SyntaxError("Symbol \'{}\' has already been declared in scope \'{}\'".format(name, self.name))

	def add_symbol(self, name, type, kind):
		self.check_symbol(name, False)

		if kind == 'field':
			kind = 'this'
		self.symbols[name] = SymbolInfo(name, type, kind, self.kindcounts[kind])
		self.kindcounts[kind] += 1

		if kind == 'static':
			name = "{}.{}".format(self.name,name)
			self.check_symbol(name, True)
			self.globalsymbols[name] = SymbolInfo(name, type, kind, self.globalcount)
			self.globalcount += 1

	def add_subroutine(self, name, type, returntype, argcount, varcount):
		gname = "{}.{}".format(self.name,name)

		self.check_symbol(name, False)
		self.check_symbol(gname, True)
		self.globalsymbols[gname] = self.symbols[name] = FunctionInfo(gname, type, returntype, argcount, varcount)


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
		actionlist.append(args)
		# if len(args) > 1:
		# 	if args[1] == 'list':
		# 		if len(args) > 2:
		# 			actionlist.append(lambda x: x.set_attribute(args[0], x.get_attribute_list(args[2:])))
		# 		else:
		# 			actionlist.append(lambda x: x.set_attribute(args[0], []))
		# 	else: #direct set
		# 		actionlist.append(lambda x: x.set_attribute(args[0], x.get_attribute(args[1])))

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
		self.symboltable = Scope()
		self.tree = Node('program', scope=self.symboltable)
		self.symboltable.node = self.tree

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

	def parse_file(self, tokens, filename):
		self.nestlevel = 0
		self.tokens = tokens
		self.idx = 0
		self.current_node = self.tree

		if self.parse('classDec'):
			self.tree.children[-1].filename = filename
			return True

		return False

	def parse(self, name, parent="None"):
		#print("PARSE: {} from {}".format(name,parent))
		#print(self.tokens[self.idx], self.tokens[self.idx+1] if self.idx < self.count-1 else "")
		if name in self.productions:
			p = self.predict(name)
			if not p:
				if self.EPS[name]:
					#print("\tGot it!")
					self.current_node.add_node(name,null=True)
					return True
				else:
					return False
			production, actionlist = p[0], p[1]

			self.nest_down(name)
			self.current_node.actionlist = actionlist
			#self.current_node.do_actions()
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

	# def build_symbols ():
	# 	for class in self.tree.children:
	# 		self.symboltable

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

	def build_symbols(self):
		for node in self.tree.children:
			if node.variables:
				node.fieldcount = 0
				for var in node.variables:
					node.scope.add_symbol(var.varname, var.type, var.kind)
					if var.kind == 'field':
						node.fieldcount+=1
			if node.subroutines:
				for sub in node.subroutines:
					argcount,varcount = 0,0
					if sub.type == 'method':
						sub.scope.add_symbol('this', 'this', 'argument')
						argcount+=1
					for param in sub.parameters or []:
						sub.scope.add_symbol(param.paramname, param.paramtype, 'argument')
						argcount+=1
					for var in sub.variables or []:
						sub.scope.add_symbol(var.varname, var.type, 'local')
						varcount+=1
					node.scope.add_subroutine(sub.subroutinename, sub.type, sub.returntype, argcount, varcount)


def get_filepaths(filename):
	path = "{}\\{}".format(sys.path[0], filename)
	paths,names = [],[]
	if os.path.isdir(path):
		for file in os.listdir(path):
			name,sep,ext = file.partition('.')
			if ext == 'jack':
				paths.append(path + '\\' + file)
				names.append(name)
	elif os.path.isfile(path):
		paths.append(path)
		names.append(filename.partition('.')[0])
		path = sys.path[0]
	else:
		print("File/Folder not found")
		exit()

	return zip(paths,names), path


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

def writefile(lines, path, name, ext):
	print("Saving as {}.{}".format(name,ext))
	filepath = "{}\\{}.{}".format(path, name, ext)
	with open(filepath, "w") as file:
		file.write(lines)


if __name__ == "__main__":
	try:
		filename = sys.argv[1]
	except IndexError:
		filename = input("File/Folder name:")
	filepaths, destpath = get_filepaths(filename)

	out = []

	s = Scanner()
	parser = Parser()

	for path,name in filepaths:
		tokens = [token for token in s.readfile(path)]
		if parser.parse_file(tokens, name):
			print("Parse successful")
			while True:
				if parser.tree.do_actions():
					break
			print("Decoration successful")
			#print(parser.tree.children[0])
			#out.append(parser.tree.get_xml())
		else:
			print("Parsing failed: {}".format(filepath))
			exit()

	parser.build_symbols()
	print("Symbol table build successful")

	writer = CodeWriter()
	files = writer.code(parser.tree)
	print("Translation successful")
	for name,lines in files:
		out = '\n'.join(lines)
		writefile(out, destpath, name, 'vm')
	#out = "\n".join(out)
	#print(out)
	filename = "out"
	#writefile(out, filename)
