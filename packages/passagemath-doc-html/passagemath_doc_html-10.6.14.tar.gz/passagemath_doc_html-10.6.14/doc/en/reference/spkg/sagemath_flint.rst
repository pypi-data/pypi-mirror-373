.. _spkg_sagemath_flint:

============================================================================================================
sagemath_flint: Fast computations with MPFI and FLINT
============================================================================================================


This pip-installable source distribution ``passagemath-flint`` provides
Cython interfaces to the ``MPFI`` and ``FLINT`` libraries.

It also ships the implementation of number fields.


What is included
----------------

* see https://github.com/passagemath/passagemath/blob/main/pkgs/sagemath-flint/MANIFEST.in


Examples
--------

A quick way to try it out interactively::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-flint[test]" ipython
    In [1]: from sage.all__sagemath_flint import *

    In [2]: RealBallField(128).pi()
    Out[2]: [3.1415926535897932384626433832795028842 +/- 1.06e-38]


Development
-----------

::

    $ git clone --origin passagemath https://github.com/passagemath/passagemath.git
    $ cd passagemath
    passagemath $ ./bootstrap
    passagemath $ python3 -m venv flint-venv
    passagemath $ source flint-venv/bin/activate
    (flint-venv) passagemath $ pip install -v -e pkgs/sagemath-flint


Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_flint`
- :ref:`spkg_gmp`
- :ref:`spkg_gmpy2`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_numpy`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_modules`
- :ref:`spkg_sagemath_ntl`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-flint ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
