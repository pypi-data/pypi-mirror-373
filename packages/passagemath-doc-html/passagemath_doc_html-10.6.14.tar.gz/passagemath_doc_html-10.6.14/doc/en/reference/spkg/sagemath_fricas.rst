.. _spkg_sagemath_fricas:

=================================================================================================================
sagemath_fricas: Symbolic computation with the general purpose computer algebra system FriCAS
=================================================================================================================


This pip-installable distribution ``passagemath-fricas`` provides an interface
to `FriCAS <https://github.com/fricas/fricas>`_, the general purpose computer
algebra system.


What is included
----------------

- `Python interface to FriCAS <https://passagemath.org/docs/latest/html/en/reference/interfaces/sage/interfaces/fricas.html>`_

- Raw access to the FriCAS executable from Python using `sage.features.fricas <https://passagemath.org/docs/latest/html/en/reference/spkg/sage/features/fricas.html>`_

- Binary wheels on PyPI contain prebuilt copies of FriCAS.


Examples
--------

Starting FriCAS from the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-fricas[test]" sage --fricas

Finding the installation location of FriCAS in Python::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-fricas[test]" ipython

    In [1]: from sage.features.fricas import FriCAS

    In [2]: FriCAS().absolute_filename()
    Out[2]: '.../bin/fricas'

Using the pexpect interface to FriCAS::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-fricas[test]" python

    >>> from sage.all__sagemath_fricas import *
    >>> fricas('1+1')
    2


Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_fricas`
- :ref:`spkg_gmp`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_ecl`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_objects`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-fricas ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
