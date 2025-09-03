.. _spkg_sagemath_nauty:

==================================================================================================================
sagemath_nauty: Find automorphism groups of graphs, generate non-isomorphic graphs with nauty
==================================================================================================================


This pip-installable distribution ``passagemath-nauty`` provides an interface to
`nauty and traces <https://pallini.di.uniroma1.it/>`_, the programs for computing
automorphism groups of graphs and digraphs by Brendan McKay and Adolfo Piperno.


What is included
----------------

- Graph generators `graphs.nauty_genbg <https://passagemath.org/docs/latest/html/en/reference/graphs/sage/graphs/graph_generators.html#sage.graphs.graph_generators.GraphGenerators.nauty_genbg>`_, `graphs.nauty_geng <https://passagemath.org/docs/latest/html/en/reference/graphs/sage/graphs/graph_generators.html#sage.graphs.graph_generators.GraphGenerators.nauty_geng>`_, `graphs.nauty_genktreeg <https://passagemath.org/docs/latest/html/en/reference/graphs/sage/graphs/graph_generators.html#sage.graphs.graph_generators.GraphGenerators.nauty_genktreeg>`_

- Hypergraph generator `hypergraphs.nauty <https://passagemath.org/docs/latest/html/en/reference/graphs/sage/graphs/hypergraph_generators.html#sage.graphs.hypergraph_generators.HypergraphGenerators.nauty>`_

- Raw access to all gtools from Python

- The binary wheels published on PyPI include a prebuilt copy of nauty and traces.


Examples
--------

Using the gtools on the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-nauty" sage -sh -c 'geng 4'
    >A geng -d0D3 n=4 e=0-6
    C?
    CC
    CE
    CF
    CQ
    CU
    CT
    CV
    C]
    C^
    C~
    >Z 11 graphs generated in 0.00 sec

Finding the installation location of a gtools program::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-nauty[test]" ipython

    In [1]: from sage.features.nauty import NautyExecutable

    In [2]: NautyExecutable('geng').absolute_filename()
    Out[2]: '/Users/mkoeppe/.local/pipx/.cache/535c90a22321f64/lib/python3.11/site-packages/sage_wheels/bin/geng'

Use with sage.graphs::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-nauty[test]" ipython

    In [1]: from sage.all__sagemath_graphs import *

    In [2]: gen = graphs.nauty_geng("7 -c")  # connected graphs on 7 vertices

    In [3]: len(list(gen))
    Out[3]: 853


Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_gmp`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_nauty`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_graphs`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-nauty ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
