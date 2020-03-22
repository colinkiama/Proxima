from lexer import Lexer 
from inbuilt import *
from errors import ProximaError 

class Enviornment:
	def __init__(self,operators):
		self.operators = operators
		self.user_def_operator = {}
		self.blocks = []
		self.variables = {}

class Block:
	def __init__(self,tokens,end='DEDENT'):
		self.tokens = []
		i=0
		while i<len(tokens) and tokens[i][0] != end:
			self.tokens.append(tokens[i])
			i+=1
	def length(self):
		return len(self.tokens)
	
	def solve(self,env):
		return eval_block(self.tokens,env)

class Brackets:
	match = {
		"RPAREN":"LPAREN",
		"RBRACK":"LBRACK",
		"RCBRACK":"LCBRACK",
	}
	def __init__(self):
		self.stk = []
	def push(self,data):
		self.stk.append(data)
	def pop(self,data):
		if len(self.stk)>0:
			if self.match[data] == self.stk[-1]:
				return self.stk.pop()
		else:
			return False

def eval_while(statement,block,env):
	while eval_block(statement,env):
		env.blocks[block].solve(env)

def eval_if(statement,block,env):
	if eval_block(statement,env):
		env.blocks[block].solve(env)

def store_oper(statement,block,env):
	if len(statement) == 1:
		env.user_def_operator[statement[0][1]] = block
	else:
		raise ProximaError('Too Many Arguments for Operator Name',statement[0][2],statement[0][3])

keys={
	'while':eval_while,
	 #'for':eval_for,
	 'operator':store_oper,
	'if':eval_if,
}

def solve_operator(operator,left,right,env):
	env.variables["left"]=left[0]
	env.variables["right"]=right[0]
	ind = env.user_def_operator[operator]
	
	env.blocks[env.user_def_operator[operator]].solve(env)
	del env.variables["left"]
	del env.variables["right"]
	if "__return__" in env.variables :
		ret = env.variables["__return__"]
		del env.variables["__return__"]
		return ret


def eval_operator(i,tokens,env):
	operator = tokens[i]
	print("operator",operator[1])
	if operator[0] == 'ASSIGN':
		var = tokens[:i]
		if len(var) != 1:
			raise ProximaError("Illegal amount of variables being assigned",tokens[i][2],tokens[i][3])
		else:
			#print(tokens[i+1:])
			#print(var)
			ret = env.variables[var[0][1]] = eval_block(tokens[i+1:],env)
			return ret

	elif operator[1] == None and tokens[i-1][1]==":": #Check if its a block with colon aand indention
		block,l = save_block(tokens,i+1,env)
		#print(tokens[1:i-1])
		#try:
		#print(tokens[0][1])
		#print(tokens[1:i-1])
		keys[tokens[0][1]](tokens[1:i-1],block,env)
		
		#except:
		#	raise ProximaError("Error ",tokens[0][2],tokens[0][3])

		i= i+l+3
		if i<len(tokens):
			#print(l,tokens[i:])
			eval_block(tokens[i+1:],env)
	else:
		#print("left")
		left = [eval_block(tokens[:i],env)]
		#print(left)
		#print("right")
		right = [eval_block(tokens[i+1:],env)]
		#print(right)
		if operator[1] != None and operator[1] in env.operators:
			#try:
				#print(left,operator[1],right)
			ret = env.operators[operator[1]](left,right,env)
				#print(env.variables)
				#print(ret)
			return ret
			#except:
			#	raise ProximaError('Error in Operator "{}"'.format(operator[1]),operator[2],operator[3])
		elif operator[1]!= None:
			#try:
				#print(left,operator[1],right)
				#print(tokens)
			ret = solve_operator(operator[1],left,right,env)
				#print(env.variables)
				#print(ret)
			return ret
			#except:
			#	raise ProximaError('Error in Operator "{}"'.format(operator[1]),operator[2],operator[3])
def eval_value(tokens,i,env):
	
	return tokens[i][1]

def eval_scope(tokens,i,env):
	end = {
		'LPAREN':'RPAREN',
		'LBRACK':'RBRACK',
		'LCBRACK':'RCBRACK',
	}

	scope = []
	end_c = end[tokens[i][0]]
	i+=1
	while i < len(tokens):
		if tokens[i][0] != end_c:
			scope.append(tokens[i])
			i+=1
		else:
			break
	if i > len(tokens):
		raise ProximaError('Brackets not complete',tokens[i-1][2],tokens[i-1][3])
	else:
		return eval_block(scope,env)

def eval_name(tokens,i,env):
	if tokens[i][1] == 'True':
		return True
	if tokens[i][1] == 'False':
		return False
	if tokens[i][1] == 'None':
		return None
	if tokens[i][1] not in env.variables:
		raise ProximaError('Variable "{}" refrenced before assignment'.format(tokens[i][1]),tokens[i][2],tokens[i][3])
		#env.variables[tokens[i][1]] = None
		#print(env.variables)
	return env.variables[tokens[i][1]]

def save_block(tokens,i,env):
	#print(tokens[i])
	if tokens[i][0] == 'INDENT':
		#print(tokens[i+1:])
		block = Block(tokens[i+1:])
		env.blocks.append(block)
		return env.blocks.index(block),block.length()

	raise ProximaError('Expected Indented block after Colon ":"',tokens[i][2],tokens[i][3])

evaluators = {
	'STRING': eval_value,
	'NUMBER': eval_value,
	'LPAREN': eval_scope,
	'LBRACK': eval_scope,
	'LCBRACK': eval_scope,
	'OPERATOR': eval_name,
}


def eval_block(tokens,env):
	
	def is_operator(token,env):
		#print(token[1])
		if (token[0] == 'OPERATOR' or token[0] == 'NEWLINE' or token[0]=='COLON' or token[0]=='ASSIGN') and (token[1] in env.operators or token[1] in env.user_def_operator):
		 	return True
		return False

	def top(op_list,env):
		for operator in env.operators.iterkeys():
			for op in op_list:
				#print(operator,op[1][1],operator==op[1][1])
				if operator == op[1][1]:
					#print(op,op_list)
					return op[0] 
		for operator in env.user_def_operator.iterkeys():
			for op in op_list:
				#print(op_list)
				#print(operator,op[1][1],operator==op[1][1])
				if operator == op[1][1]:
					#print(op,op_list)
					return op[0] 

	def find_operator(tokens,env):
		i = 0
		bc = 0
		op_list = []
		bc_stk = Brackets()
		while  i < len(tokens):
			#print(tokens[i],is_operator(tokens[i],env))
			if is_operator(tokens[i],env) and bc == 0:
				op_list.append((i,tokens[i]))
			elif tokens[i][0] == 'LPAREN' or tokens[i][0] == 'LBRACK' or tokens[i][0] == 'LCBRACK':
				bc+=1
				bc_stk.push(tokens[i][0])
			elif tokens[i][0] == 'RPAREN' or tokens[i][0] == 'RBRACK' or tokens[i][0] == 'RCBRACK':
				if bc_stk.pop(tokens[i][0]):
					bc-=1
				else:
					raise ProximaError('Extra Brackets "{}"'.format(tokens[i][1]),tokens[i][2],tokens[i][3])

			i+=1
		if len(tokens) == 0:
			return -1
		else:
			#print(op_list)
			return top(op_list,env)

	#check if the operator is open
	i = find_operator(tokens,env)
	#if operator open evaluate
	if i >= 0 :
		#print(tokens[i])
		return eval_operator(i,tokens,env)
	# else iterate over each token
	if len(tokens)>0:
		#print('boss' in env.user_def_operator)
		i = 0
		return evaluators[tokens[i][0]](tokens,i,env)

	return None

def evaluate(code):
	#print(code)
	lexer = Lexer()
	tokens = lexer.tokenize(code)
	'''
	for t in tokens:
		print(t)
	'''
	env = Enviornment(operators)

	eval_block(tokens[:len(tokens)-1],env)	
	#print(env.variables)