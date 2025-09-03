.. _spkg_sagemath_combinat:

==============================================================================================================================
sagemath_combinat: Algebraic combinatorics, combinatorial representation theory
==============================================================================================================================


This pip-installable source distribution ``passagemath-combinat`` is a distribution of a part of the Sage library.  It provides a subset of the modules of the Sage library ("sagelib", ``passagemath-standard``).


What is included
----------------

* `Enumerative Combinatorics <https://passagemath.org/docs/latest/html/en/reference/combinat/sage/combinat/enumerated_sets.html#sage-combinat-enumerated-sets>`_: `Partitions, Tableaux <https://passagemath.org/docs/latest/html/en/reference/combinat/sage/combinat/catalog_partitions.html>`_

* `Combinatorics on Words <https://passagemath.org/docs/latest/html/en/reference/combinat/sage/combinat/words/all.html#sage-combinat-words-all>`_, `Free Monoids <https://passagemath.org/docs/latest/html/en/reference/monoids/index.html>`_, `Automatic Semigroups <https://passagemath.org/docs/latest/html/en/reference/monoids/sage/monoids/automatic_semigroup.html>`_

* `Symmetric Functions <https://passagemath.org/docs/latest/html/en/reference/combinat/sage/combinat/sf/all.html#sage-combinat-sf-all>`_, other `Algebras with combinatorial bases <https://passagemath.org/docs/latest/html/en/reference/algebras/index.html>`_

* see https://github.com/passagemath/passagemath/blob/main/pkgs/sagemath-combinat/MANIFEST.in


Examples
--------

A quick way to try it out interactively::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-combinat[test]" ipython

    In [1]: from sage.all__sagemath_combinat import *

    In [2]: RowStandardTableaux([3,2,1]).cardinality()
    Out[2]: 60


Available as extras, from other distribution packages
-----------------------------------------------------

* `passagemath-graphs <https://pypi.org/project/passagemath-graphs>`_:
  Graphs, posets, finite state machines, combinatorial designs, incidence structures, quivers

* `passagemath-modules <https://pypi.org/project/passagemath-modules>`_:
  Modules and algebras, root systems, coding theory

* `passagemath-polyhedra <https://pypi.org/project/passagemath-polyhedra>`_:
  Polyhedra, lattice points, hyperplane arrangements


Development
-----------

::

    $ git clone --origin passagemath https://github.com/passagemath/passagemath.git
    $ cd passagemath
    passagemath $ ./bootstrap
    passagemath $ python3 -m venv combinat-venv
    passagemath $ source combinat-venv/bin/activate
    (combinat-venv) passagemath $ pip install -v -e pkgs/sagemath-combinat


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
- :ref:`spkg_gmpy2`
- :ref:`spkg_memory_allocator`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_setuptools`
- :ref:`spkg_symmetrica`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-combinat ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
