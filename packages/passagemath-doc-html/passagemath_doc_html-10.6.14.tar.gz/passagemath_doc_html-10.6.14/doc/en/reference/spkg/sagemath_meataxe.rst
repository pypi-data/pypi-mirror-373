.. _spkg_sagemath_meataxe:

================================================================================================================
sagemath_meataxe: Matrices over small finite fields with meataxe
================================================================================================================


This pip-installable distribution ``passagemath-meataxe`` is a small
optional distribution for use with ``passagemath-standard``.

This distribution provides the SageMath modules ``sage.libs.meataxe``
and ``sage.matrix.matrix_gfpn_dense``.

It provides a specialized implementation of matrices over the finite field F_q, where
q <= 255, using the `SharedMeatAxe <http://users.minet.uni-jena.de/~king/SharedMeatAxe/>`_
library.


Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_meataxe`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_modules`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-meataxe ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
