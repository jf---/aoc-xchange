
tests
-----
include tests with different geometries (open shell, curves etc ...)
step_ocaf
Python 3 tests
doctests?
brep importer and exporter tests
auto folder creation option in checks.py/check_exporter_filename()

iges
----
extract iges version when importing
roots and shapes -> have a look at iges file format spec
build the shell and solid from connected faces (pretty complicated / network theory / find groups of interconnected faces)

step_ocaf
---------
complete review + tests
looks weird to only consider compounds and solids while reading file. What about edges etc ...

issues
------
importing iges box -> 24 edges
importing step box -> 12 edges

Later
-----

opennurbs
  -> python bindings (cf. https://github.com/raj12lnm/OpenNurbs-Python) with pybindgen (or swig?)
        cython can be used to wrao existing codebases (and libraries for automation exist)
        https://github.com/cython/cython/wiki/AutoPxd
  -> work from/to 3dm files
  -> cage editing available in opennurbs?