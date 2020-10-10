"""
Parse a "tau testcase".
Previously implemented here: https://github.com/koo5/univar/blob/master/tau.cpp
and here: https://github.com/koo5/univar/blob/master/pyin/tau2.py
"""


import logging,json
import shlex
import pathlib
from enum import Enum, auto
from .locators import *
from .dotdict import Dotdict
from .recursive_file_includer import *


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

def bn(conn, suffix = ''):
	"""this is kind of the worst of both worlds. It requires the roundtrip to obtain an unused bnode id from the triplestore (although those are fetched in bulk and cached - see ValueFactory.BLANK_NODE_AMOUNT).
	and it returns an uri, so, lists will not be serialized in a nice way.
	"""
	if suffix != '':
		suffix = '_' + suffix
	return 'https://rdf.localhost/bn/'+conn.createBNode().id[2:] + suffix


def tell_if_is_last_element(x):
	for i, j in enumerate(x):
		yield j, (i == (len(x) - 1))


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

#def _to_dict_recursively(ns, s, graph):
def _to_dict_recursively(ns, s):
	"""this problem wouldn't exist in js. That is, dict keys can be written with dot notation, in js, so no need for Dotdict."""
	if isinstance(s, Dotdict):
		s = s._dict
	#This problem would exist, because the keys need to conform to some basic IRI pattern to be accepted by json-ld. I think it might be better if triplestores etc accepted strings for predicates. But since we are here already, we might as well come up with some good namespace here. It will be kinda ridiculous that there might be predicates in that namespace that mean different things in different places, but hey, that's json.
	if isinstance(s, dict):
		r = {}
		for k,v in s.items():
			r[ns + ':' + k] = _to_dict_recursively(ns, v)
		return r
	#just a required, mechanical translation into json-ld. A json list, in json-ld, means a set. Actually, that's really silly, because it complicates going from json to rdf, and is only useful for representing (complex-beyond-json) rdf in json-ld, right? which is something nobody really cares about, you can pick any other serialization, right? Do we really care about dumbing things back down into json? (i dont, right now)
	#---
	#well, another issue turned up, agraph always stores list triples in default graph, no matter what.
	elif isinstance(s, list):
		r = []
		for i in s:
			r.append(_to_dict_recursively(ns, i))
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
		c = Context(f, fn, conn)
		c.set_mode(Mode.COMMANDS)
		c.set_setting('result_limit', 123)
		return c.interpret(graph)



class Context:
	"""
	a Context is something like a current input channel. You could invoke the parser/runner with a bunch of command line arguments. A context would be created to parse those arguments. One of them is a .tau file, so a nested context would be created for it, and so on. Irc/interactive input is also considered. None of this is implemented in this version though, and i don't think i'll bother with it so i should probably change the design here...
	"""

	def __init__(self, input, base_uri, conn):
		#format = "";
		#base = "";
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
		d0 = _to_dict_recursively('xx', self.data)
		d0['@id'] = uid
		# d = {
		# 	"@id": graph,
  		# 	"@graph":[d0]
  		# }
		d = d0
		logging.getLogger(__name__).info(f'#saving: {json.dumps(d,indent=2)}')
		logging.getLogger(__name__).info(f'#saving: {d}')
		#fixme:
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


# todo: could we replace the tau format with https://github.com/Keats/scl ?
