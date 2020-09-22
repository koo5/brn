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
	EVAL = auto()
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
	mode: Mode

	def set_setting(k,v):
		logging.getLogger(__name__).info(f'#{k} = {human_friendly_x(v)}')
		self.setting[k] = v

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
					
				else:
					self.rdf_lines.append(l)

	def process_command_tokens(self):
		while len(self.tokens):
			token = self.tokens.pop(0)




def print_test_success(x:bool):
    dout << INPUT->name << ":test:";
    if (x)
        dout << KGRN << "PASS" << KNRM << endl;
    else
        dout << KRED << "FAIL" << KNRM << endl;
}

def count_fins_in_input_text(input_text):
	...

