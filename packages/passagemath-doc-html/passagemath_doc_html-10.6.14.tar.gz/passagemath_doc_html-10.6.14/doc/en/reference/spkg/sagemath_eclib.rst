.. _spkg_sagemath_eclib:

======================================================================================================================
sagemath_eclib: Elliptic curves over the rationals with eclib/mwrank
======================================================================================================================


This pip-installable distribution ``passagemath-eclib`` provides the
Cython interface to John Cremona's programs for enumerating and computing
with elliptic curves defined over the rational numbers.


What is included
----------------

- `Sage interface to Cremona’s eclib library (also known as mwrank) <https://passagemath.org/docs/latest/html/en/reference/libs/sage/libs/eclib/interface.html>`_

- `Cython interface to Cremona’s eclib library (also known as mwrank) <https://passagemath.org/docs/latest/html/en/reference/libs/sage/libs/eclib/mwrank.html>`_

- `Cremona matrices <https://passagemath.org/docs/latest/html/en/reference/libs/sage/libs/eclib/mat.html>`_

- `Modular symbols using eclib newforms <https://passagemath.org/docs/latest/html/en/reference/libs/sage/libs/eclib/newforms.html>`_

- `Cremona modular symbols <https://passagemath.org/docs/latest/html/en/reference/libs/sage/libs/eclib/homspace.html>`_

- `Cremona modular symbols (constructor) <https://passagemath.org/docs/latest/html/en/reference/libs/sage/libs/eclib/constructor.html>`_

- `Interface to the mwrank program <https://passagemath.org/docs/latest/html/en/reference/interfaces/sage/interfaces/mwrank.html#module-sage.interfaces.mwrank>`_


Examples
--------

A quick way to try it out interactively::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-eclib[test]" ipython

    In [1]: from sage.all__sagemath_eclib import *

    In [2]: M = CremonaModularSymbols(43, cuspidal=True); M
    Out[2]: Cremona Cuspidal Modular Symbols space of dimension 6 for Gamma_0(43) of weight 2 with sign 0

Finding the installation location of the mwrank program::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-eclib" python
    >>> from sage.features.eclib import Mwrank
    >>> Mwrank().absolute_filename()
    '.../bin/mwrank'

Use with `sage.schemes.elliptic_curves <https://passagemath.org/docs/latest/html/en/reference/arithmetic_curves/index.html#elliptic-curves>`_::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-eclib[test]" ipython

    In [1]: from sage.all__sagemath_eclib import *

    In [2]: x = polygen(ZZ, 'x')

    In [3]: K = NumberField(x**2 + 23, 'a'); a = K.gen()

    In [4]: E = EllipticCurve(K, [0,0,0,101,0])

    In [5]: E.gens()


Development
-----------

::

    $ git clone --origin passagemath https://github.com/passagemath/passagemath.git
    $ cd passagemath
    passagemath $ ./bootstrap
    passagemath $ python3 -m venv eclib-venv
    passagemath $ source eclib-venv/bin/activate
    (eclib-venv) passagemath $ pip install -v -e pkgs/sagemath-eclib


Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_eclib`
- :ref:`spkg_gmp`
- :ref:`spkg_memory_allocator`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_flint`
- :ref:`spkg_sagemath_linbox`
- :ref:`spkg_sagemath_modules`
- :ref:`spkg_sagemath_ntl`
- :ref:`spkg_sagemath_objects`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-eclib ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
