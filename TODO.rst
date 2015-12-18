
dataexchange
------------
tests
    include tests with different geometries (open shell, curves etc ...)
roundtrip (open file and save it -> check everything is ok (colors, layers etc ...)


iges
----
extract iges version when importing
roots and shapes -> have a look at iges file format spec

********importing a box.igs + dump_topology -> the same entities appear 6 times ! (likely hiccup in read_file() loop with
******** roots and shapes), yet, topo.number_of_faces() gives the right number (6)

******** some entities get imported multiple times

build the shell and solid from connected faces (pretty complicated / network theory / find groups of interconnected faces)

step
----

extract topology in importer: solids, shells based on shapes list content