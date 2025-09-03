.. _spkg_sagemath_lrslib:

=======================================================================================================
sagemath_lrslib: Reverse search for vertex enumeration and convex hulls with lrslib
=======================================================================================================


This pip-installable distribution ``passagemath-lrslib`` provides an interface
to `lrslib <http://cgm.cs.mcgill.ca/~avis/C/lrs.html>`_ by David Avis,
an implementation of the reverse search algorithm for vertex enumeration
and convex hull problems.


What is included
----------------

* Binary wheels on PyPI contain prebuilt copies of lrslib executables.


Examples
--------

Using lrslib programs on the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-lrslib" sage -sh -c lrs
    *lrs:lrslib v.7.1 2021.6.2(64bit,lrslong.h,hybrid arithmetic)

Finding the installation location of an lrslib program::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-lrslib[test]" ipython

    In [1]: from sage.features.lrs import LrsNash

    In [2]: LrsNash().absolute_filename()
    Out[2]: '/Users/mkoeppe/.local/pipx/.cache/db3f5a0e2996f81/lib/python3.11/site-packages/sage_wheels/bin/lrsnash'

Use with `sage.game_theory <https://passagemath.org/docs/latest/html/en/reference/game_theory/index.html>`_::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-lrslib[test]" ipython

    In [1]: from sage.all__sagemath_lrslib import *

    In [2]: A = matrix([[1, -1], [-1, 1]]); B = matrix([[-1, 1], [1, -1]])

    In [3]: matching_pennies = NormalFormGame([A, B])

    In [4]: matching_pennies.obtain_nash(algorithm='lrs')
    Out[4]: [[(1/2, 1/2), (1/2, 1/2)]]


Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_gmp`
- :ref:`spkg_lrslib`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_objects`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-lrslib ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
