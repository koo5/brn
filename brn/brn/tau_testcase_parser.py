"""
Parse a "tau" testcase file.
Previously implemented here: https://github.com/koo5/univar/blob/master/tau.cpp
and here: https://github.com/koo5/univar/blob/master/pyin/tau2.py
"""


import logging,json
import shlex, stat
import pathlib
from enum import Enum, auto
from .locators import *
from .dotdict import Dotdict
from .recursive_file_includer import *
from .sparql_helper import bn

# def showtriples(conn):
# 	statements = conn.getStatements()
# 	with statements:
# 		for statement in statements:
# 			logging.getLogger(__name__).info(f'quad({statement})')

def is_file(p):
	p = pathlib.Path(p)
	return stat.S_ISREG(os.lstat(p)[stat.ST_MODE]) and not p.is_dir()

def find_all_files_recursively(path: Path):

	path.value = pathlib.Path(path.value)

	paths = []

	if is_file(path.value):
		paths.append(path.value)
	for p in path.value.rglob('*'):
		if is_file(p):
			paths.append(p)
	return [ Path(x) for x in sorted(paths) ]


def human_friendly_setting_value(x):
	try:
		return x.name
	except:
		return x

def tell_if_is_last_element(x):
	for i, j in enumerate(x):
		yield j, (i == (len(x) - 1))

def element_by_index_upper_clipped(array, index):
	if len(array) > index:
		return array[index]
	else:
		return array[-1]

# def add_list(l, graph):
# 	"""
# 	must be a list of uris. It would be helpful to start using some URI/Bnode classes here, perhaps the ones from the agraph package.
# 	"""
# 	bn0 = bn('cell')
# 	bn = bn0
# 	q = []
# 	for i, is_last in tell_if_is_last_element(l):
# 		q.append('<'+bn+'> rdf:first <' + i + '>.')
# 		if is_last:
# 			bn_next = "http://www.w3.org/1999/02/22-rdf-syntax-ns#nil"
# 		else
# 			bn_next = bn('cell')
# 		bn0 = bn('cell')
# 		q.append('<'+bn+'> rdf:rest <' + bn_next + '>.')
# 		bn = bn_next
# 	insert = """INSERT DATA
# 	{
# 		GRAPH <"""+graph+""">
# 		{
# 			""" + "\n".join(q) + """
# 		}
# 	}"""
# 	conn.
# 	return bn0



def _to_dict_recursively(s):
	"""this problem wouldn't exist in js. That is, dict keys can be written with dot notation, in js, so no need for Dotdict."""
	if isinstance(s, Dotdict):
		s = s._dict
	#This problem would exist, because the keys need to conform to some basic IRI pattern to be accepted by json-ld. I think it might be better if triplestores etc accepted strings for predicates. But since we are here already, we might as well come up with some good namespace here. It will be kinda ridiculous that there might be predicates in that namespace that mean different things in different places, but hey, that's json.
	if isinstance(s, dict):
		r = {}
		for k,v in s.items():
			r[k] = _to_dict_recursively(v)
		return r
	#just a required, mechanical translation into json-ld. A json list, in json-ld, means a set. Actually, that's really silly, because it complicates going from json to rdf, and is only useful for representing (complex-beyond-json) rdf in json-ld, right? which is something nobody really cares about, you can pick any other serialization, right? Do we really care about dumbing things back down into json? (i dont, right now)
	#---
	#well, another issue turned up, agraph always stores list triples in default graph, no matter what.
	elif isinstance(s, list):
		r = []
		for i in s:
			r.append(_to_dict_recursively(i))
		return {'@list':r}
	#custom types like this might fare better in js too, but idk yet..
	elif isinstance(s, pathlib.Path):
		return str(s)
	else:
		return s


class ParsingError(Exception):
	pass


class Mode(Enum):
	COMMANDS = auto()
	KB = auto()
	QUERY = auto()
	SHOULDBE = auto()
	SHOULDBEERROR = auto()



def parse_testcase(conn, p: Path, graph):
	fn = p.value
	logging.getLogger(__name__).info(f'parsing {fn}')
	assert isinstance(fn, pathlib.PosixPath)
	with fn.open() as f:
		c = Context(fn, f, fn, conn)
		c.set_mode(Mode.COMMANDS)
		c.set_setting('result_limit', 123)
		return c.interpret(graph)

def text_with_line_numbers(text):
	r = []
	for lineno,line in enumerate(text.split('\n')):
		r.append(str(lineno+1) + ':'+ line)
	return '\n'.join(r)



class Context:
	"""
	a Context is something like a current input channel. You could invoke the parser/runner with a bunch of command line arguments. A context would be created to parse those arguments. One of them is a .tau file, so a nested context would be created for it, and so on. Irc/interactive input is also considered. None of this is implemented in this version though, and i don't think i'll bother with it so i should probably change the design here...
	"""

	def __init__(self, fn, input, base_uri, conn):
		#format = "";
		#base = "";
		self.fn = fn
		self.conn = conn
		self.input = input
		self.base_uri = base_uri
		self.mode_stack = []
		"""
		one Context/input/tau-testcase-file produces one test "setup", here stored in self.data. Such "setup" has multiple kb_texts and multiple queries, each which an optional shouldbe. 
		"""
		self.data = Dotdict({'queries': []})
		self.settings = Dotdict()
		self.common_text = []
		self.rdf_lines = []
		self.kb_texts = []

	@property
	def mode(self):
		return self.mode_stack[-1]

	def set_mode(self, mode):
		self.mode_stack.append(mode)
		self.print_setting('mode', self.mode)

	def set_setting(self, k, v):
		self.print_setting(k,v)
		self.settings[k] = v

	def print_setting(self, k,v):
		logging.getLogger(__name__).debug(f'#{k} = {human_friendly_setting_value(v)}')

	def interpret(self, graph):
		for l in self.input:
			if self.mode == Mode.COMMANDS:
				ls = l.lstrip()
				if ls == '':
					continue
				if ls.startswith('#'):
					continue
				if ls.startswith('@'):
					if ls.startswith('@include'):
						tokens = shlex.split(ls)
						self.common_text.extend(self.lexically_include_file(tokens[1]))
					else:
						"""the "header", before any commands, is allowed include @prefix or other @ declarations. It will be prepended to everything"""
						self.common_text.append(l)
					continue
				try:
					self.tokens = shlex.split(l)
				except Exception as e:
					raise ParsingError(f'when tokenizing {l.__repr__()}:'+str(e))
				self.process_command_tokens()
			else:
				l2 = l.strip()
				if l2 == 'fin.':
					self.on_complete_rdf_text(self.base_uri)
					self.mode_stack.pop()
				else:
					if is_include_line(l2):
						tokens = shlex.split(l2)
						self.rdf_lines.extend(self.lexically_include_file(tokens[1]))
					self.rdf_lines.append(l)
		return self.save_testcase(graph)



	def save_testcase(self, graph):#, , unique_uri_generator):
		uid = bn(self.conn, 'testcase')
		#uid = 'https://rdf.localhost/bn/' + uid.id
		d = _to_dict_recursively(self.data)
		d['@id'] = uid
		d['@context'] = {'@vocab':'https://rdf.lodgeit.net.au/testcase/'}
		logging.getLogger(__name__).debug(f'#saving: {json.dumps(d,indent=2)}')
		#logging.getLogger(__name__).info(f'#saving: {d}')
		#fixme, use agraph IRI term or something:
		self.conn.addData(d, context='<'+graph+'>')
		logging.getLogger(__name__).info(f'#saved testcase IRI: {uid}')
		#showtriples(self.conn)
		return uid


	def process_command_tokens(self):
		while len(self.tokens):
			token = self.tokens.pop(0)
			if token == 'kb':
				self.set_mode(Mode.KB)
			elif token == 'query':
				self.set_mode(Mode.QUERY)
			elif token == 'shouldbe':
				self.set_mode(Mode.SHOULDBE)
			elif token == 'shouldbetrue':
				"""means that,
				in backward chaining, the query should succeed
				in forward chaining, it should be possible to unify the query graph with a subset of the result graph
				"""
			elif token == 'shouldbeerror':
				self.set_mode(Mode.SHOULDBEERROR)
			elif token == 'thatsall':
				"""
				a thatsall means that the runner should wait for further results from the reasoner, or for its termination. That is, it should check that the engine doesn't come up with more answers. If a thatsall is not present in a testcase file, this means that additional answers are allowed.
				"""
				self.data.queries[-1].more_answers_forbidden = True
			elif is_url(token):
				self.rdf_lines = open('token').readlines()
				self.on_complete_rdf_text(token)
			else:
				raise ParsingError(f'unrecognized token: {token.__repr__()}')

	def n3_text(self,text,base_uri):
		text = ''.join(text)
		x = text_with_line_numbers(text)
		return Dotdict({'text':text,'base_uri':base_uri,'text_with_line_numbers':x})

	def on_complete_rdf_text(self,base_uri):
		full_n3_text = self.full_n3_text(base_uri)
		self.rdf_lines = []
		if self.mode == Mode.KB:
			self.kb_texts.append(full_n3_text)
		if self.mode == Mode.QUERY:
			tc = Dotdict()
			self.data.queries.append(tc)
			self.last_textcase = tc
			tc['@id'] = bn(self.conn, 'testcase')
			tc.type = {'@id':'query'}
			tc.kb_texts = self.kb_texts
			tc.query_text = full_n3_text
			tc.source_file = self.fn
		if self.mode == Mode.SHOULDBE:
			if self.last_textcase == None:
				raise err
			self.last_textcase.shouldbe_text = full_n3_text
		if self.mode == Mode.SHOULDBEERROR:
			if self.last_textcase == None:
				raise err
			self.last_textcase.shouldbeerror_text = ''.join(self.rdf_lines)

	def full_n3_text(self,base_uri):
		return self.n3_text(self.common_text+self.rdf_lines,base_uri)


# todo: could we replace the tau format with https://github.com/Keats/scl ?
