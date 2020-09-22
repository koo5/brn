import logging
import os
from .locators import *
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


def parse_testcase(p: Path):
	logging.getLogger(__name__).info(f'parsing {p.value}')
	
