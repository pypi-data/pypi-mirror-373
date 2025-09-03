.. _spkg_sagemath_macaulay2:

===========================================================================================================================
sagemath_macaulay2: Computing in commutative algebra, algebraic geometry and related fields with Macaulay2
===========================================================================================================================


This pip-installable distribution ``passagemath-macaulay2`` provides an interface to
`Macaulay2 <https://github.com/Macaulay2/M2>`_.


What is included
----------------

- `Python interface to Macaulay 2 <https://passagemath.org/docs/latest/html/en/reference/interfaces/sage/interfaces/macaulay2.html>`_

- The binary wheels published on PyPI include a prebuilt copy of Macaulay 2.


Examples
--------

Using Macaulay 2 on the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-macaulay2" sage -sh -c 'M2'

Finding the installation location of Macaulay 2::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-macaulay2[test]" ipython

    In [1]: from sage.features.macaulay2 import Macaulay2

    In [2]: Macaulay2().absolute_filename()
    Out[2]: '.../bin/M2'

Using the Python interface::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-macaulay2[test]" ipython

    In [1]: from sage.all__sagemath_macaulay2 import *

    In [2]: R = macaulay2('QQ[x, y]'); R
    Out[2]: QQ[x..y]

    In [3]: S = R / macaulay2('ideal {x^2 - y}'); S
    Out[3]:
    QQ[x..y]
    --------
      2
     x  - y

    In [4]: S.gens()
    Out[4]: {x, y}


Available as extras, from other distributions
---------------------------------------------

Jupyter kernel
~~~~~~~~~~~~~~

``pip install "passagemath-macaulay2[jupyterkernel]"``
 installs the kernel for use in the Jupyter notebook and JupyterLab

``pip install "passagemath-macaulay2[notebook]"``
 installs the kernel and the Jupyter notebook

``pip install "passagemath-macaulay2[jupyterlab]"``
 installs the kernel and JupyterLab


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
- :ref:`spkg_macaulay2`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_flint`
- :ref:`spkg_sagemath_modules`
- :ref:`spkg_sagemath_objects`
- :ref:`spkg_sagemath_repl`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-macaulay2 ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
