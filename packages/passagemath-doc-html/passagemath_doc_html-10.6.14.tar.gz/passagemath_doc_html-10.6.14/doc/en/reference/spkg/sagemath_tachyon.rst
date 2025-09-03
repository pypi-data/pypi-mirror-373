.. _spkg_sagemath_tachyon:

================================================================================
sagemath_tachyon: Interface to the ray tracing system tachyon
================================================================================


This pip-installable source distribution ``passagemath-tachyon`` provides an interface to
the ray tracing system `tachyon <http://jedi.ks.uiuc.edu/~johns/raytracer/>`_.


Examples
--------

A quick way to try it out interactively::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-tachyon[test]" ipython

    In [1]: from sage.all__sagemath_tachyon import *


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
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_objects`
- :ref:`spkg_setuptools`
- :ref:`spkg_tachyon`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-tachyon ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
