.. _spkg_sagemath_palp:

===================================================================================================
sagemath_palp: Lattice polytopes and applications to toric geometry with PALP
===================================================================================================


This pip-installable source distribution ``passagemath-palp`` provides
an interface to the `Package for Analyzing Lattice Polytopes <http://hep.itp.tuwien.ac.at/~kreuzer/CY/CYpalp.html>`__ (PALP)
by M. Kreuzer and H. Skarke, a set of C programs for calculations
with lattice polytopes and applications to toric geometry.


What is included
----------------

- The binary wheels published on PyPI include a prebuilt copy of PALP.


Examples
--------

Using PALP programs on the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-palp" sage -sh -c 'echo "14 2 3 4 5" | class.x -f -po zbin'
    0kR-0 0MB 0kIP 0kNF-0k 5_13 v8r8 f10r10 10b6 0s 0u 0n
    14 2 3 4 5 R=152 +0sl hit=0 IP=276 NF=179 (0)
    Writing zbin: 152+0sl 0m+0s 644b  u36 done: 0s

Finding the installation location of a PALP program::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-palp[test]" ipython

    In [1]: from sage.features.palp import PalpExecutable

    In [2]: PalpExecutable("poly", 5).absolute_filename()
    Out[2]: '/Users/mkoeppe/.local/pipx/.cache/db3f5a0e2996f81/lib/python3.11/site-packages/sage_wheels/bin/poly-5d.x'

Use with sage.geometry::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-palp[test]" ipython

    In [1]: from sage.all__sagemath_polyhedra import *

    In [2]: square = lattice_polytope.cross_polytope(2).polar()

    In [3]: square.points()
    Out[3]:
    N( 1,  1),
    N( 1, -1),
    N(-1, -1),
    N(-1,  1),
    N(-1,  0),
    N( 0, -1),
    N( 0,  0),
    N( 0,  1),
    N( 1,  0)
    in 2-d lattice N


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
- :ref:`spkg_palp`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-palp ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
