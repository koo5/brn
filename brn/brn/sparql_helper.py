
import logging, os
import franz.openrdf.model
import franz.openrdf.model.literal
from franz.openrdf.connect import ag_connect
from franz.openrdf.vocabulary.rdf import RDF
from pyld import jsonld



conn = None

pointer_namespaces = {
	'rdf':RDF.NAMESPACE,
	'rdf2':'https://rdf.lodgeit.net.au/rdf2/'}

def ensure_common_namespaces_are_defined(conn):
	conn.setNamespace('rdf2', 'https://rdf.lodgeit.net.au/rdf2/')
	conn.setNamespace('localhost', 'https://rdf.localhost/')

def my_ag_conn(clear=False):
	global conn
	if not conn:
		host=os.environ['SEMANTIC_DESKTOP_AGRAPH_HOST']
		port=os.environ['SEMANTIC_DESKTOP_AGRAPH_PORT']
		logging.getLogger(__name__).info(f'connecting to {host}:{port}...')
		conn = ag_connect(
			repo=os.environ['SEMANTIC_DESKTOP_AGRAPH_REPO'],
			host=host,
			port=port,
			user=os.environ['SEMANTIC_DESKTOP_AGRAPH_USER'],
			password=os.environ['SEMANTIC_DESKTOP_AGRAPH_PASS'],
			clear=clear
			)
		logging.getLogger(__name__).info(f'connected.')
		ensure_common_namespaces_are_defined(conn)
	return conn


def select_one_result_and_one_binding(conn, query_str):
	# unfortunately, the nice table you get when you pass "output=True" is generated on the server, triggered by setting the accept header to "text/table"
	query_str2 = "SELECT * WHERE {\n" + query_str + "}"
	query = conn.prepareTupleQuery(query=query_str2)
	return select_one_result(conn, query)[0]

def select_one_result(conn, query):
	with query.evaluate() as results:
		results_list = list(results)
	if len(results_list) != 1:
		raise Exception(f'expected one result. query: {query.queryString}\n,got:{results_list}')
	return results_list[0]


def franz_term_to_pyld(ft):
	if isinstance(ft, franz.openrdf.model.URI):
		return {'type': 'IRI', 'value': ft.value}
	if isinstance(ft, franz.openrdf.model.BNode):
		return {'type': 'blank node', 'value': '_:' + ft.id}
	if isinstance(ft, franz.openrdf.model.literal.Literal):
		r = {'type': 'literal', 'value': ft.label}
		r['language'] = ft.language
		r['datatype'] = ft.datatype
		return r
	raise Exception(f'unsupported type of term: {ft}')


def franz_quad_to_pyld(franz_quad):
	"""franz_quad: as gotten from conn.getStatements."""
	return {
		'subject':franz_term_to_pyld(franz_quad.subject),
		'predicate':franz_term_to_pyld(franz_quad.predicate),
		'object':franz_term_to_pyld(franz_quad.object)}

def read_quads_from_context(conn, graph):
	quads = []
	with conn.getStatements(
			contexts=[graph],
			tripleIDs=True
		) as statements:
			statements.enableDuplicateFilter()
			for statement in statements:
				#print(statement)
				quads.append(franz_quad_to_pyld(statement))
	return quads

def frame_result(jld, result):
	frame = {
			"@context": {
				"xsd": "http://www.w3.org/2001/XMLSchema#",
				"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
				"rdfs": "http://www.w3.org/2000/01/rdf-schema#",
				'tc':'https://rdf.lodgeit.net.au/testcase/'
			},
			#'@type':'https://rdf.lodgeit.net.au/tau_testcase_parser/Result'
			'@id':franz_term_to_pyld(result)['value']
		}
	data = jsonld.frame(jld, frame, {'omitGraph':False,'embed':'@always'})
	#print(json.dumps(data,indent=4))
	return data

def construct_pointer(conn, iri, graph):
	id = bn(conn, 'pointer')
	conn.addData({
		'@context':pointer_namespaces,
		'@id':id,
		'rdf:value': {'@id':iri},
		'rdf2:data_is_in_graph': {'@id':graph}})
	return id

def read_pointer(conn, pointer):
	# what if the data is not in a graph? maybe we'll be able to CONSTRUCT one? todo.
	query = conn.prepareTupleQuery(query="""
			SELECT * WHERE {
			   ?pointer rdf:value ?result .	   
			   OPTIONAL {?pointer rdf2:data_is_in_graph ?graph}
			}""")
	query.setBinding('pointer', pointer)
	print(query)
	r = select_one_result(conn, query)
	graph = r['graph']
	result = r['result']
	return graph, result


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

