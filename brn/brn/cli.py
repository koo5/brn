#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the entry point for the command-line interface (CLI) application.
.. currentmodule:: brn.cli
.. moduleauthor:: koo <my_email@gmail.com>
"""

import logging
import click

from .version import __version__

#import pdb; pdb.set_trace()
from .tau_testcase_parser import *
from .locators import *
from franz.openrdf.connect import ag_connect
import os


class Info(object):
	"""An information object to pass data between CLI functions."""

	def __init__(self):  # Note: This object must have an empty constructor.
		"""Create a new instance."""
		# self.verbose: int = 0
		pass


# pass_info is a decorator for functions that pass 'Info' objects.
#: pylint: disable=invalid-name
pass_info = click.make_pass_decorator(Info, ensure=True)



@click.group()
@click.option("--verbose", "-v", count=True, help="Enable verbose output.")
@pass_info
def cli(info: Info, verbose: int):
	"""Run brn."""
	verbosity = verbose
	del verbose

	"""
	user sets verbosity, with how many -v's they invoke the command with, but python logging is based on filtering by severity level.
	the more verbose, the less severity required of a log message to display it.
	"""
	VERBOSITY_to_SEVERITY = [
		logging.FATAL,
		logging.INFO,
		logging.DEBUG,
		logging.NOTSET # NOTSET should be the last
	]  #: a mapping of `verbosity` option counts to logging levels.
	logging.basicConfig(
		level=element_by_index_upper_clipped(VERBOSITY_to_SEVERITY, verbosity)
	)
	if verbosity > 0:
		click.echo(click.style(
			f"Logging severity filter level: {logging.getLogger().getEffectiveLevel()}",
			fg="yellow"#, blink=True
		))



@cli.command()
@pass_info
@click.argument('main_directory', type=click.Path())
def parse_tau_testcases(_: Info, main_directory):
	"""Parse tau testcases in all subdirectories of main_directory.
	main_directory is probably tests/."""
	logging.getLogger(__name__).info("scanning " + main_directory)
	paths = find_all_files_recursively(AbsPath(main_directory))
	logging.getLogger(__name__).info(f'found files: {paths}')
	with ag_connect(
			repo=os.environ['SEMANTIC_DESKTOP_AGRAPH_REPO'],
			host=os.environ['SEMANTIC_DESKTOP_AGRAPH_HOST'],
			port=os.environ['SEMANTIC_DESKTOP_AGRAPH_PORT'],
			user=os.environ['SEMANTIC_DESKTOP_AGRAPH_USER'],
			password=os.environ['SEMANTIC_DESKTOP_AGRAPH_PASS'],
			clear=True
			) as conn:
		print (conn.size())
		for i in paths:
			parse_testcase(conn, i)





@cli.group()
def cli2():
	"""Run cli2."""
	pass


@cli2.command()
def version():
	"""Get the library version."""
	click.echo(click.style(f"{__version__}", bold=True))







