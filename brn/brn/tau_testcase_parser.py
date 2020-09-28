"""
parse a "tau testcase". previously implemented here: https://github.com/koo5/univar/blob/master/tau.cpp
and here: https://github.com/koo5/univar/blob/master/pyin/tau2.py





"""


import logging
import shlex
import pathlib
from enum import Enum, auto
from .locators import *
from .dotdict import Dotdict

def showtriples(conn):
	statements = conn.getStatements()
	with statements:
		for statement in statements:
			logging.getLogger(__name__).info(f'quad({statement})')

def find_all_files_recursively(path: Path):
	paths = []
	for p in pathlib.Path(path.value).rglob('*'):
		if not p.is_dir():
			paths.append(p)
	return [ Path(x) for x in sorted(paths) ]


def element_by_index_upper_clipped(array, index):
	if len(array) > index:
		return array[index]
	else:
		return array[-1]

def human_friendly_setting_value(x):
	try:
		return x.name
	except:
		return x


def is_url(x):
	if x.startswith('http://'):
		return True
	if x.startswith('file://'):
		return True


def _to_dict_recursively(ns, s):
	if isinstance(s, Dotdict):
		s = s._dict
	if isinstance(s, dict):
		r = {}
		for k,v in s.items():
			r[ns + ':' + k] = _to_dict_recursively(ns, v)
		return r
	elif isinstance(s, list):
		r = []
		for i in s:
			r.append(_to_dict_recursively(ns, i))
		return {'@list':r}
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



def parse_testcase(conn, p: Path):
	fn = p.value
	logging.getLogger(__name__).info(f'parsing {fn}')
	assert isinstance(fn, pathlib.PosixPath)
	with fn.open() as f:
		c = Context(f, fn, conn)
		c.set_mode(Mode.COMMANDS)
		c.set_setting('result_limit', 123)
		c.interpret()


class Context:
	"""
	format = "";
	base = "";
	"""

	def __init__(self, input, base_uri, conn):
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
		logging.getLogger(__name__).info(f'#{k} = {human_friendly_setting_value(v)}')

	def interpret(self):
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
					if l2.startswith('@include'):
						tokens = shlex.split(l2)
						self.rdf_lines.extend(self.lexically_include_file(tokens[1]))
					self.rdf_lines.append(l)
		self.save_testcase()

	def lexically_include_file(self, path):
		return open(path).readlines()

	def save_testcase(self):
		d = _to_dict_recursively('xx:', self.data)
		uid = self.conn.createBNode()
		self.data['@id'] = uid
		logging.getLogger(__name__).info(f'#saving: {d}')
		self.conn.addData(d)
		logging.getLogger(__name__).info(f'#saved testcase IRI: {uid}')
		showtriples(self.conn)


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

	def on_complete_rdf_text(self,base_uri):
		text = '\n'.join(self.rdf_lines)
		self.rdf_lines = []
		logging.getLogger(__name__).info(f'#on_complete_rdf_text:\n{text}')
		if self.mode == Mode.KB:
			self.kb_texts.append(Dotdict({'text':text,'base_uri':base_uri}))
		if self.mode == Mode.QUERY:
			tc = Dotdict()
			self.data.queries.append(tc)
			self.last_textcase = tc
			tc.type = 'query'
			tc.kb_texts = self.kb_texts
			tc.query_text = text
		if self.mode == Mode.SHOULDBE:
			if self.last_textcase == None:
				raise err
			self.last_textcase.shouldbe_text = text
		if self.mode == Mode.SHOULDBEERROR:
			if self.last_textcase == None:
				raise err
			self.last_textcase.shouldbeerror_text = text
