just a simple parser of a simple reasoner testcase format. Next i will be adding the executor. Why is this overcomplicated by storing intermediate data in a triplestore rather than flinging around unstructured text? Program 1 doesn't have to worry about where to save temporary files and what arguments to invoke program 2 with, the indirection is gone, is just asserts a description of the task at hand, and the other program just grabs it and runs. I try to explain here: https://github.com/software-for-immortality/software-for-immortality.github.io/blob/master/writings/1.md

also possibly of interest: https://linkeddatafragments.org/concept/#tpf https://gnome.pages.gitlab.gnome.org/tracker/docs/developer/ https://www.researchgate.net/publication/228854943_Tracking_rdf_graph_provenance_using_rdf_molecules https://github.com/koo5/hackery2/blob/master/src/data/notes/rdf_forms.txt ...

It should be noted that the graph is essentially application-specific, rather than datatype-specific. Iow, the graph is constructed for the purpose of processing the data in some way, by some application. Any links to/from inside the graph to the outside are ignored by such application...

"tracker 3 made it fairly easy to make federated queries, and create endpoints out of your apps. Sounds like a good fit :)"



krunner

etc
