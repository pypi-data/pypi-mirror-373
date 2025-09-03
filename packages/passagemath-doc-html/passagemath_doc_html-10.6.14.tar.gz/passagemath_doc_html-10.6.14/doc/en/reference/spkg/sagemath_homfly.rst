.. _spkg_sagemath_homfly:

==================================================================================================================
sagemath_homfly: Homfly polynomials of knots/links with libhomfly
==================================================================================================================


This pip-installable distribution ``passagemath-homfly`` provides a Cython interface
to the `libhomfly <https://github.com/miguelmarco/libhomfly>`_ library.


What is included
----------------

* `sage.libs.homfly <https://github.com/passagemath/passagemath/blob/main/src/sage/libs/homfly.pyx>`_


Examples
--------

::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-homfly[test]" ipython

    In [1]: from sage.libs.homfly import homfly_polynomial_dict

    In [2]: trefoil = '1 6 0 1  1 -1  2 1  0 -1  1 1  2 -1 0 1 1 1 2 1'

    In [3]: homfly_polynomial_dict(trefoil)
    Out[3]: {(-4, 0): -1, (-2, 0): -2, (-2, 2): 1}


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
- :ref:`spkg_libhomfly`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_objects`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-homfly ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
