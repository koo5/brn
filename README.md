what i'll be doing is running automated tests of a program i am developing. The testcases and corresponding expected outputs are stored in a convenient textual file format i call ".tau".

i go through a couple steps:

start allegrograph triplestore:

~/sw/agraph-7.0.3/agraph-7.0.3/agraph-control start

if needed, set the env vars so that programs know how to access it:

../conf/set_my_agraph_env_vars.fish 

an alternative would be to use a system-wide database, like Tracker.

next, i could just run the command, give it a directory of testcase files, and wait for the results. But i can also run each phase separately. First phase is parsing the text files and storing the results in a structured format (RDF):
	
```
koom@dev ~/brnkacka/brn (master)> brn -v internal parse-tau-testcases ../tau-tests/tests/
20.046 scanning ../tau-tests/tests/
20.048 found files: [Path(PosixPath('../tau-tests/tests/agda/0')), Path(PosixPath('../tau-tests/tests/agda/a')), Path(PosixPath('../tau-tests/tests/agda/bool')), Path(PosixPath('../tau-tests/tests/existentials/addition2')), Path(PosixPath('../tau-tests/tests/existentials/addition3')), Path(PosixPath('../tau-tests/tests/existentials/ep')), Path(PosixPath('../tau-tests/tests/existentials/fff')), Path(PosixPath('../tau-tests/tests/existentials/natxxx'))]
20.048 connecting to 127.0.0.1:10035...
20.062 connected.
20.108 parsing ../tau-tests/tests/agda/0
20.116 #saved testcase IRI: https://rdf.localhost/bn/DF9BEE0x25217_testcase
20.116 parsing ../tau-tests/tests/agda/a
20.122 #saved testcase IRI: https://rdf.localhost/bn/DF9BEE0x25215_testcase
20.122 parsing ../tau-tests/tests/agda/bool
20.132 #saved testcase IRI: https://rdf.localhost/bn/DF9BEE0x25213_testcase
20.132 parsing ../tau-tests/tests/existentials/addition2
20.167 #saved testcase IRI: https://rdf.localhost/bn/DF9BEE0x25240_testcase
20.168 parsing ../tau-tests/tests/existentials/addition3
20.190 #saved testcase IRI: https://rdf.localhost/bn/DF9BEE0x25329_testcase
20.190 parsing ../tau-tests/tests/existentials/ep
20.219 #saved testcase IRI: https://rdf.localhost/bn/DF9BEE0x25353_testcase
20.220 parsing ../tau-tests/tests/existentials/fff
20.225 #saved testcase IRI: https://rdf.localhost/bn/DF9BEE0x25352_testcase
20.226 parsing ../tau-tests/tests/existentials/natxxx
20.234 #saved testcase IRI: https://rdf.localhost/bn/DF9BEE0x25350_testcase
20.249 #saved result IRI: https://rdf.localhost/bn/DF9BEE0x25349_result with list:[{'x:id': 7, '@id': 'https://rdf.localhost/bn/DF9BEE0x25350_testcase'}, {'x:id': 6, '@id': 'https://rdf.localhost/bn/DF9BEE0x25352_testcase'}, {'x:id': 5, '@id': 'https://rdf.localhost/bn/DF9BEE0x25353_testcase'}, {'x:id': 4, '@id': 'https://rdf.localhost/bn/DF9BEE0x25329_testcase'}, {'x:id': 3, '@id': 'https://rdf.localhost/bn/DF9BEE0x25240_testcase'}, {'x:id': 2, '@id': 'https://rdf.localhost/bn/DF9BEE0x25213_testcase'}, {'x:id': 1, '@id': 'https://rdf.localhost/bn/DF9BEE0x25215_testcase'}, {'x:id': 0, '@id': 'https://rdf.localhost/bn/DF9BEE0x25217_testcase'}]
20.249 #note:due to agraph bug, the list items appear in reverse order here^
20.271 #saved testcases IRI: https://rdf.localhost/bn/DF9BEE0x25450_pointer
```

the last line tells us how to find the results in the database. Next, i run the second phase of the pipeline, the program takes some command-line arguments that i have to provide by hand, but the crux of the data is pointed to by the --iri parameter.

```
koom@dev ~/brnkacka/brn (master)> 
brn internal  run-testcases2 --limit-testcase-count 1 --executable ~/lodgeit2/master2/sources/public_lib/lodgeit_solvers/prolog/pyco3/pyco3_in_devrunner.sh --profile  pyco3  --halt-on-error true  --iri https://rdf.localhost/bn/DF9BEE0x24085_pointer
```

that's where this walkthrough unfortunately has to end, because this step is still work in progress:)

