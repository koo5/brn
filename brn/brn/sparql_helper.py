
import logging
import franz.openrdf.model
import franz.openrdf.model.literal


def select_one_result_and_one_binding(conn, query_str):
	# unfortunately, the nice table you get when you pass "output=True" is generated on the server, triggered by setting the accept header to "text/table"
	query_str2 = "SELECT * WHERE {\n" + query_str + "}"
	query = conn.prepareTupleQuery(query=query_str2)
	return select_one_result(conn, query)[0]

def select_one_result(conn, query, query_str):
	with query.evaluate() as results:
		results_list = list(results)
	if len(results_list) != 1:
		raise Exception(f'expected one result. query: {query_str}\n,got:{results_list}')
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
