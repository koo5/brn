from fastapi import FastAPI

app = FastAPI()

# @app.post("/perform")
# def perform(task_uri: str, graph_uri: str):
# 	import tau3_n3logic0
# 	import sparql_helper
# 	conn = my_ag_conn()
# 	return {"item_id": 5}

@app.post("/parse_tau3_n3logic0")
def perform(text_uri: str, text_graph: str):
	import tau3_n3logic0
	import sparql_helper
	conn = my_ag_conn()
	text_uri tc:text (Text^^_) text_graph
	text_uri tc:base_uri, (Base_uri^^_) text_graph
	tau3_n3logic0.load0(kb_text, goal_text, base)
	return {"item_id": 5}
