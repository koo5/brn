#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

"""
This is the entry point for the command-line interface (CLI) application.
.. currentmodule:: brn.cli
.. moduleauthor:: koo <my_email@gmail.com>
"""

import logging, subprocess
import click, shlex
from .version import __version__
from .tau_testcase_parser import *
from .locators import *
from .sparql_helper import *
from pyld import jsonld
import franz.openrdf.model




def configure_logger(verbosity):
	logging.getLogger("urllib3").setLevel(logging.WARNING)
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

	lvl = element_by_index_upper_clipped(VERBOSITY_to_SEVERITY, verbosity)

	logging.basicConfig(
		level=lvl
	)

	formatter = logging.Formatter('%(asctime)s %(message)s')
	formatter.default_time_format = '%S'
	formatter.default_msec_format = '%s.%03d'
	root_logger = logging.getLogger()
	#root_logger.setLevel(lvl)
	root_handler = root_logger.handlers[0]
	root_handler.setFormatter(formatter)
	#logging.getLogger(__name__).handlers[0].setFormatter(formatter)

	if verbosity > 10:
		logging.getLogger(__name__).info(f"Logging severity filter level: {logging.getLogger().getEffectiveLevel()}")




@click.group()
@click.option("--verbose", "-v", count=True, help="increase verbosity.")
def cli(verbose: int):
	"""brn is a toplevel interface that will possibly include multiple subcommands for automation and testing. warning: There are some experiments going on under the hood.."""
	configure_logger(verbose)



@cli.command()
def version():
	"""Get the library version."""
	click.echo(click.style(f"{__version__}", bold=True))


file_formats_info = """
you can specify the rdf format with the --format processing directive
"""


@cli.command(help='hh')
@click.option('--profile', '-p', type=str)
@click.option('--executable', type=click.Path(readable=True, exists=True, dir_okay=False))
@click.option('--halt-on-error', type=bool, default=False)
@click.option('--limit-testcase-count', type=int, default=None)
@click.argument('tau_files', nargs=1, type=click.Path(readable=True, exists=True), required=True)
@click.pass_context
def run_testcases(ctx, profile, executable, halt_on_error, limit_testcase_count, tau_files):
	iri = ctx.invoke(parse_tau_testcases, tau_files=tau_files)
	ctx.invoke(run_testcases2, profile=profile, executable=executable, halt_on_error=halt_on_error, limit_testcase_count=limit_testcase_count, iri=iri)






@cli.group()
def internal():
	"""internal commands."""
	pass



@internal.command()
@click.argument('tau_files', nargs=1, type=click.Path(readable=True, exists=True, file_okay=False), required=True)
def parse_tau_testcases(tau_files):
	"""Parse tau testcases in all subdirectories of main_directory.
	main_directory is probably ../tau-tests/tests/ ."""
	logging.getLogger(__name__).info("scanning " + tau_files)
	paths = find_all_files_recursively(Path(tau_files))
	logging.getLogger(__name__).info(f'found files: {paths}')

	conn = my_ag_conn()

	# ok this will need some serious explaining/visualization, like a screenshot of the generated graph
	graph = bn(conn, 'graph')
	uris = []
	for id,i in enumerate(paths):
		uris.append({'x:id':id,'@id':parse_testcase(conn, i, graph)})

	# seems like a bug in agraph jsonld, lists with uris are reversed. we should probably do the translation from json-ld with pyld instead.
	uris.reverse()

	# <result> <rdf:value> <list> <graph>
	# <list> <rdf:first> xxx <graph>
	# <list> <rdf:rest> xxx <graph>...
	result = bn(conn, 'result')
	conn.addData({
				'@id':result,
				'@type':'https://rdf.lodgeit.net.au/tau_testcase_parser/Result',
				RDF.VALUE:{'@list':uris}
		}, context='<'+graph+'>')

	logging.getLogger(__name__).info(f'#saved result IRI: {result} with list:{uris}')
	logging.getLogger(__name__).info(f'#note:due to agraph bug, the list items appear in reverse order here^')

	# <pointer> <rdf:value> <result> <default>
	# <pointer> <data_is_in_graph> <graph> <default>
	pointer = bn(conn, 'pointer')
	conn.addData({
		'@id':pointer,
		RDF.VALUE:{'@id':result},
		'https://rdf.lodgeit.net.au/rdf2/data_is_in_graph': {'@id':graph}
	})

	# <last_tau_testcases_parsed> <rdf:value> <pointer> <default graph>
	# i guess it's silly to use agraph's json-ld logic, it's buggy anyway, and if we just did the conversion of this object into the triple ourselves, we could have a replaceTriple() naturally.
	conn.remove(franz.openrdf.model.URI('https://rdf.localhost/last_tau_testcases_parsed'), RDF.VALUE, None)
	conn.addData({
		'@id':'https://rdf.localhost/last_tau_testcases_parsed',
		RDF.VALUE:{'@id':pointer}
	})

	logging.getLogger(__name__).info(f'#saved testcases IRI: {pointer}')
	conn
	return pointer



@internal.command()
@click.option('--profile', '-p', type=str)
@click.option('--executable', type=click.Path(readable=True, exists=True, dir_okay=False))
@click.option('--halt-on-error', type=bool, default=False)
@click.option('--limit-testcase-count', type=int, default=None)
@click.option('--iri', nargs=1, type=str, required=False, help="the IRI of the testcase sequence. If omitted, rdf:value of localhost:last_tau_testcases_parsed is used")
def run_testcases2(profile, executable, halt_on_error, limit_testcase_count, iri):
	conn = my_ag_conn()
	ensure_common_namespaces_are_defined(conn)
	if iri == None:
		pointer = select_one_result_and_one_binding(conn, "localhost:last_tau_testcases_parsed rdf:value ?pointer.")
	else:
		pointer = franz.openrdf.model.URI(iri)
		#pointer = iri
	print(pointer)
	graph, result = read_pointer(conn,pointer)
	quads = read_quads_from_context(conn,graph)
	jld = jsonld.from_rdf({'@default':quads},{})

	data = frame_result(jld,result)
	testcases=data['@graph'][0]['rdf:value']['@list']
	for tc_idx, tc in enumerate(testcases):
		if tc_idx == limit_testcase_count:
			break
		queries = tc['tc:queries']['@list']
		for q in queries:
			query_pointer_uri = construct_pointer(conn, q, graph)
			#query_pointer_uri is a single uri, and you can read the default graph to figure out the value it points to, and what the relevant graph is

			if profile == 'pyco3':
				if executable == None:
					executable = 'pyco3'

			args = [executable, '-g', 'main', '--', '--task', query_pointer_uri]
			logging.getLogger(__name__).info(f'#spawning: {shlex.join(args)}')
			cmpl = subprocess.run(args)

			if halt_on_error:
				if cmpl.returncode != 0:
					exit()



# 			while True:
# 				q(task_uri, has_processing, X),
# 				q(X, has_status, S),
# 				if S == failed:
# 					q(X has_error E)
# 				else:
# 					if S == succeded:
# 						q(X, has_results, Results_list),
# 						rdf_list_length(Results_list)



