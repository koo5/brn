from ordered_and_indexed_store import OrderedAndIndexedStore
import rdflib
from notation3 import BadSyntax
from io import StringIO


IMPLIES = rdflib.URIRef("http://www.w3.org/2000/10/swap/log#implies")



def parse_n3_text_into_ordered_store(string, identifier, publicID):
	"""
	* identifier:
	The Graph constructor can take an identifier which identifies the Graph
    by name.  If none is given, the graph is assigned a BNode for its
    identifier.

    * publicID:
    the logical URI to use as the document base. If None
    specified the document location is used (at least in the case where
    there is a document location).
	"""
	graph = rdflib.Graph(store=OrderedAndIndexedStore(), identifier=identifier)
	graph.parse(data=string, format='n3', publicID=publicID)
	return graph



def load0(kb_text, goal_text, base):
	kb = StringIO(kb_text)
	goal = StringIO(goal_text)
	return pyin.load(kb, goal, base)

def load(kb_stream, goal_stream, base):

	store = OrderedAndIndexedStore()
	kb_graph = rdflib.Graph(store=store, identifier=base)
	kb_conjunctive = rdflib.ConjunctiveGraph(store=store, identifier=base)
	kb_graph.parse(source=kb_stream, format='n3', publicID=base)

	# if not nolog:
	# 	log('---kb:')
	# 	try:
	# 		for l in kb_graph.serialize(format='n3').splitlines():
	# 			log(l.decode('utf8'))
	# 	except Exception as e:
	# 		log(str(e))
	# 	log('---kb quads:')
	# 	for l in kb_conjunctive.serialize(format='nquads').splitlines():
	# 		log(l.decode('utf8'))
	# 	log('---')

	def fixup3(o):
		if isinstance(o, rdflib.Graph):
			return URIRef('file:///#' + o.identifier.n3().strip('_:'))
		return o
	def fixup2(o):
		if type(o) == rdflib.BNode:
			return rdflib.Variable(str(o.lower()))
		return o
	def fixup(spo):
		s,p,o = spo
		return (fixup2(s), fixup2(p), fixup2(o))

	rules = []
	head_triples_triples_id = 0
	kb_graph_triples = [fixup(x) for x in kb_graph.triples((None, None, None))]
	facts = GraphTuple(Triple(un_move_me_ize_pred(fixup3(x[1])),[fixup3(x[0]),fixup3(x[2])]) for x in kb_graph_triples)
	facts.id=head_triples_triples_id
	head_triples_triples_id += 1
	for kb_graph_triple_idx,(s,p,o) in enumerate(kb_graph_triples):
		if p == IMPLIES:
			body = Graph()
			head_triples = [fixup(x) for x in kb_conjunctive.triples((None, None, None, o))]
			head_triples_triples = Graph()
			for triple in [Triple(fixup3(x[1]),[fixup3(x[0]),fixup3(x[2])]) for x in head_triples]:
				move = False
				if triple.pred == URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#move_me_to_body_first'):
					triple.pred = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#first')
					move = True
				if triple.pred == URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#move_me_to_body_rest'):
					triple.pred = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#rest')
					move = True
				if move:
					body.append(triple)
				else:
					head_triples_triples.append(triple)
			for body_triple in [fixup(x) for x in kb_conjunctive.triples((None, None, None, s))]:
				body.append(Triple((un_move_me_ize_pred(fixup3(body_triple[1]))), [fixup3(body_triple[0]), fixup3(body_triple[2])]))
			#body.reverse()
			to_expand = []
			for triple in head_triples_triples + body:
				for thing in triple.args:
					if type(thing) == rdflib.Variable:
						if str(thing).endswith('_'):
							to_expand.append(thing)
			for thing in to_expand:
				body.insert(0,Triple(rdflib.RDF.first, [thing, rdflib.Variable(str(thing)[:-1]+'f')]))
				body.insert(0,Triple(rdflib.RDF.rest , [thing, rdflib.Variable(str(thing)[:-1]+'r')]))
			body = GraphTuple(body)
			head_triples_triples = GraphTuple(head_triples_triples)
			head_triples_triples.id=head_triples_triples_id
			head_triples_triples_id += 1
#			if len(head_triples_triples) > 1:
#				with open(_rules_file_name, 'a') as ru:
#					ru.write("expanded rules for " + head_triples_triples.str(shorten) + ":\n")
			for head_triple_idx in range(len(head_triples_triples)):
				rules.append(Rule(head_triples_triples, head_triple_idx, body))
			if len(head_triples_triples) > 1:
				with open(_rules_file_name, 'a') as ru:
					ru.write("\n\n")
		else:
			rules.append(Rule(facts, kb_graph_triple_idx, GraphTuple()))

	goal_rdflib_graph = rdflib.ConjunctiveGraph(store=OrderedStore(), identifier=base)
	goal_rdflib_graph.parse(goal_stream, format='n3', publicID=base)

	if not nolog:
		log('---goal:')
		try:
			for l in goal_rdflib_graph.serialize(format='n3').splitlines():
				log(l.decode('utf8'))
		except Exception as e:
			log(str(e))
		log('---goal nq:')
		for l in goal_rdflib_graph.serialize(format='nquads').splitlines():
			log(l.decode('utf8'))
		log('---')

	goal = Graph()
	for s,p,o in [fixup(x) for x in goal_rdflib_graph.triples((None, None, None, None))]:
		goal.append(Triple(un_move_me_ize_pred(fixup3(p)), [fixup3(s), fixup3(o)]))
	#goal.reverse()
	goal = GraphTuple(goal)
	query_rule = Rule(GraphTuple(), None, goal)
	return rules, query_rule, goal














def used_rules_by_pred(rules, query):
	"""
	filter out unused rules, return the rest as a dict by pred
	"""
	preds = defaultdict(list)
	for rule in rules:
		pred = rule.head.pred
		use = False
		for rule2 in rules + [query]:
			for bi in rule2.body:
				if bi.pred == pred:
					use = True
		if use:
			preds[pred].append(rule)
	return preds





	#
	# try:
	#
	# except BadSyntax as e:
	# 	echo(':test:parsing failed in:')
	# 	echo(data)
	# 	echo(str(e))
	# 	fail()
	# return graph


