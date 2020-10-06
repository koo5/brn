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
from franz.openrdf.vocabulary.rdf import RDF
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
	"""brn is a toplevel interface that will possibly include multiple subcommands for automation and testing. warning: There are some experiments going on under the hood.."""
	configure_logger(verbose)


def configure_logger(verbosity):
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
		logging.getLogger(__name__).info(f"Logging severity filter level: {logging.getLogger().getEffectiveLevel()}")

def my_ag_connect():
	host=os.environ['SEMANTIC_DESKTOP_AGRAPH_HOST']
	port=os.environ['SEMANTIC_DESKTOP_AGRAPH_PORT']
	logging.getLogger(__name__).info(f'connecting to {host}:{port}...')
	return ag_connect(
			repo=os.environ['SEMANTIC_DESKTOP_AGRAPH_REPO'],
			host=host,
			port=port,
			user=os.environ['SEMANTIC_DESKTOP_AGRAPH_USER'],
			password=os.environ['SEMANTIC_DESKTOP_AGRAPH_PASS'],
			clear=True
			)
	logging.getLogger(__name__).info(f'connected.')

@cli.command()
@pass_info
@click.argument('main_directory', nargs=1, type=click.Path(readable=True, exists=True, file_okay=False), required=True)
def parse_tau_testcases(_: Info, main_directory):
	"""Parse tau testcases in all subdirectories of main_directory.
	main_directory is probably tau-tests/."""
	logging.getLogger(__name__).info("scanning " + main_directory)
	paths = find_all_files_recursively(AbsPath(main_directory))
	logging.getLogger(__name__).info(f'found files: {paths}')
	with my_ag_connect() as conn:
		uris = []
		for i in paths:
			uris.append(parse_testcase(conn, i))
		conn.addData({
			"@id": "http://franz.com/mygraph1",
  			"@graph":
  			[
	  			{
					'@id':'https://rdf.localhost/last_tau_testcases_parsed',
					RDF.VALUE:{'@list':uris}
				}
			]
		})



@cli.group()
def cli2():
	"""Run cli2."""
	pass


@cli2.command()
def version():
	"""Get the library version."""
	click.echo(click.style(f"{__version__}", bold=True))



@cli.command()
@click.argument('profile', nargs=1, type=str, required=True)
@click.argument('executable', nargs=1, type=click.Path(readable=True, exists=True, dir_okay=False), required=False)
@click.argument('IRI', nargs=1, type=str)

def run_testcases(profile, executable, iri):
	pass
	# with my_ag_connect() as conn:
	# 	#if iri == None:
	# 		#iri =statements = conn.getStatements(
	# 	logging.getLogger(__name__).info(f': {iri}')
	# 	for testcase in iterate_rdf_list(iri):
	# 		if profile == 'pyco3':
	# 			subprocess.spawn([executable, '--task', task_uri])
	# 			while True:
	# 				q(task_uri, has_processing, X),
	# 				q(X, has_status, S),
	# 				if S == failed:
	# 					q(X has_error E)
	# 				else:
	# 					if S == succeded:
	# 						q(X, has_results, Results_list),
	# 						rdf_list_length(Results_list)
