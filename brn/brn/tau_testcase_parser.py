import logging
import shlex
import pathlib
from enum import Enum, auto
from locators import *
from dotdict import Dotdict

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


class Mode(Enum):
	COMMANDS = auto()
	KB = auto()
	QUERY = auto()
	SHOULDBE = auto()



def parse_testcase(p: Path):
	fn = p.value
	logging.getLogger(__name__).info(f'parsing {fn}')
	assert isinstance(fn, pathlib.PosixPath)
	with fn.open() as f:
		c = Context(f)
		c.set_mode(Mode.COMMANDS)
		c.set_setting('result_limit', 123)
		c.interpret()


class Context:
	"""
	format = "";
	base = "";
	"""
	def __init__(self, input):
		self.input = input
		self.mode_stack = []
		self.data = {'testcases': []}
		self.settings = Dotdict()

	def set_mode(self, mode):
		self.mode_stack.push(mode)
		self.print_setting('mode', self.mode)

	def set_setting(self, k, v):
		self.print_setting(k,v)
		self.settings[k] = v

	def self.print_setting(self, k,v):
		logging.getLogger(__name__).info(f'#{k} = {human_friendly_setting_value(v)}')

	def human_friendly_setting_value(x):
		try:
			return x.name
		except:
			return x

	def interpret():
		while l = f.readline():
			if self.mode == Mode.COMMANDS:
				self.tokens = shlex.split(l)
				self.process_command_tokens()
			else:
				l2 = l.strip()
				if l2 == 'fin.':
					self.on_complete_rdf_text()
					self.mode_stack.pop()
				else:
					self.rdf_lines.append(l)

	def process_command_tokens(self):
		while len(self.tokens):
			token = self.tokens.pop(0)

	def on_complete_rdf_text(self):
		text = '\n'.join(self.rdf_lines)
		print('on_complete_rdf_text ' + text)
		if self.mode == Mode.KB:
			self.kb_text = text
		if self.mode == Mode.QUERY:
			tc = Dotdict()
			self.data.testcases.append(tc)
			self.last_textcase = tc
			tc.type = PYCO.query
			tc.kb_text = self.kb_text
			tc.query_text = text
		if self.mode == Mode.SHOULDBE:
			if self.last_textcase == None:
				raise err
			self.last_textcase.shouldbe_text = text
