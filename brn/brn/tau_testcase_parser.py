import logging
from locators import *
import pathlib

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




query_counter = 0
input_text = ""


from enum import Enum, auto

class Mode(Enum):
	COMMANDS = auto()
	KB = auto()
	QUERY = auto()
	SHOULDBE = auto()


format = "";
base = "";


def parse_testcase(p: Path):
	fn = p.value
	logging.getLogger(__name__).info(f'parsing {fn}')
	assert isinstance(fn, pathlib.PosixPath)
	c = Context()
	c.set_setting('mode', Mode.COMMANDS)
	c.set_setting('result_limit', 123)
	with fn.open() as f:
		c.input = f
		input.interpret(f)

import shlex

class Context:
	def __init__(self):
		self.mode_stack = [Mode.COMMANDS]

	def set_setting(k,v):
		logging.getLogger(__name__).info(f'#{k} = {human_friendly_setting_value(v)}')
		self.setting[k] = v

	def human_friendly_setting_value(x):
		try:
			return x.name
		except:
			return x

	def pop_token(line:str):
		line = line.strip()
		if not len(line):
			return ''
		tokens = shlex.split(line)
		tokens[0]





	def interpret():
		while l = f.readline():
			if self.mode == Mode.COMMANDS:
				self.tokens = shlex.split(l)
				self.process_command_tokens()
			else:
				l2 = l.strip()
				if l2 == 'fin.':
					on_complete_rdf_text()
					self.mode_stack.pop()
				else:
					self.rdf_lines.append(l)

	def process_command_tokens(self):
		while len(self.tokens):
			token = self.tokens.pop(0)

	def on_complete_rdf_text(self, data):
		text = '\n'.join(self.rdf_lines)
		print('on_complete_rdf_text ' + text)
		if self.mode == Mode.KB:
			self.kb_text = text
		if self.mode == Mode.QUERY:
			tc = Dotdict()
			data.testcases.append(tc)
			self.last_textcase = tc
			tc.type = PYCO.query
			tc.kb_text = self.kb_text
			tc.query_text = text
		if self.mode == Mode.SHOULDBE:
			if self.last_textcase == None:
				raise err
			self.last_textcase.shouldbe_text = text
