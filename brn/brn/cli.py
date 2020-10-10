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
from .sparql_helper import *
import rdflib
from pyld import jsonld
import json




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

def my_ag_connect(clear=False):
	host=os.environ['SEMANTIC_DESKTOP_AGRAPH_HOST']
	port=os.environ['SEMANTIC_DESKTOP_AGRAPH_PORT']
	logging.getLogger(__name__).info(f'connecting to {host}:{port}...')
	return ag_connect(
			repo=os.environ['SEMANTIC_DESKTOP_AGRAPH_REPO'],
			host=host,
			port=port,
			user=os.environ['SEMANTIC_DESKTOP_AGRAPH_USER'],
			password=os.environ['SEMANTIC_DESKTOP_AGRAPH_PASS'],
			clear=clear
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
	with my_ag_connect(clear=True) as conn:
		# ok this will need some serious explaining/visualization
		graph = bn(conn, 'graph')
		uris = []
		for id,i in enumerate(paths):
			uris.append({'x:id':id,'@id':parse_testcase(conn, i, graph)})

		# seems like a bug in agraph jsonld, lists with uris are reversed.
		uris.reverse()

		#conn.addData({'@id':'http://xxx', RDF.VALUE:{'@list':['a','b']}})

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

		# uris = [
		# 	{'@id':'http://yy.yy','http://yy.vvv':'a'},
		# 	{'@id':'http://yy.zz','http://zz.vvv':'b'}
		# ]
		#
		# conn.addData({
		# 	"@id": graph,
  		# 	"@graph":
  		# 	[
	  	# 		{
		# 			'@id':result,
		# 			'@type':'https://rdf.lodgeit.net.au/tau_testcase_parser/Result',
		# 			RDF.VALUE:{'@list':uris}
		# 		}
		# 	]
		# })
		#
		# logging.getLogger(__name__).info(f'#saved result IRI: {result} with list:{uris}')

		# <pointer> <rdf:value> <result> <default>
		# <pointer> <data_is_in_graph> <graph> <default>
		pointer = bn(conn, 'pointer')
		conn.addData({
			'@id':pointer,
			RDF.VALUE:{'@id':result},
			'https://rdf.lodgeit.net.au/rdf2/data_is_in_graph': {'@id':graph}
		})

		# <last_tau_testcases_parsed> <rdf:value> <pointer> <default graph>
		conn.addData({
			'@id':'https://rdf.localhost/last_tau_testcases_parsed',
			RDF.VALUE:{'@id':pointer}
		})

		logging.getLogger(__name__).info(f'#saved testcases IRI: {pointer}')


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
@click.argument('IRI', nargs=1, type=str, required=False)

def run_testcases(profile, executable, iri):
	with my_ag_connect() as conn:
		ensure_common_namespaces_are_defined(conn)
		if iri == None:
			pointer = select_one_result_and_one_binding(conn, "localhost:last_tau_testcases_parsed rdf:value ?pointer.")
		else:
			pointer = '<'+iri+'>'
		graph, result = read_pointer(conn,pointer)
		quads = read_quads_from_context(conn,graph)
		jld = jsonld.from_rdf({'@default':quads},{})

		data = frame_result(jld,result)
		testcases=data['@graph'][0]['rdf:value']['@list']
		for tc in testcases:
			if profile == 'pyco3':
				if executable == None:
					executable = 'pyco3'
			queries = tc['xx:queries']['@list']
			for q in queries:
				for 


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

def frame_result(jld, result):
	frame = {
			"@context": {
				"xsd": "http://www.w3.org/2001/XMLSchema#",
				"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
				"rdfs": "http://www.w3.org/2000/01/rdf-schema#"
			},
			#'@type':'https://rdf.lodgeit.net.au/tau_testcase_parser/Result'
			'@id':franz_term_to_pyld(result)['value']
		}
	data = jsonld.frame(jld, frame, {'omitGraph':False,'embed':'@always'})
	print(json.dumps(data,indent=4))
	return data

def read_quads_from_context(conn, graph):
	quads = []
	with conn.getStatements(
			contexts=[graph],
			tripleIDs=True
		) as statements:
			statements.enableDuplicateFilter()
			for statement in statements:
				print(statement)
				quads.append(franz_quad_to_pyld(statement))
	return quads

def read_pointer(conn, pointer):
	# what if the data is not in a graph? maybe we'll be able to CONSTRUCT one? todo.
	query = conn.prepareTupleQuery(query="""
			SELECT * WHERE {
			   ?pointer rdf:value ?result .
			   # data_is_in_graph should eventually be optional.
			   ?pointer rdf2:data_is_in_graph ?graph .
			}""")
	query.setBinding('pointer', pointer)
	r = select_one_result(conn, query)
	graph = r['graph']
	result = r['result']
	return graph, result

def ensure_common_namespaces_are_defined(conn):
	conn.setNamespace('rdf2', 'https://rdf.lodgeit.net.au/rdf2/')
	conn.setNamespace('localhost', 'https://rdf.localhost/')


