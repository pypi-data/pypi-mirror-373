.. _spkg_sagemath_bliss:

======================================================================================================
sagemath_bliss: Graph (iso/auto)morphisms with bliss
======================================================================================================


This pip-installable package ``passagemath-bliss`` is a distribution of a part of the Sage Library.  It provides a small subset of the modules of the Sage library ("sagelib", ``passagemath-standard``).

It provides a Cython interface to the `bliss <https://users.aalto.fi/~tjunttil/bliss/index.html>`_ library for the purpose
of computing graph (iso/auto)morphisms.


What is included
----------------

* see https://github.com/passagemath/passagemath/blob/main/pkgs/sagemath-bliss/MANIFEST.in


Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_bliss`
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
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

    passagemath-bliss ~= 10.6.14.0

Equivalent System Packages
--------------------------

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install sagemath-bliss


However, these system packages will not be used for building Sage
because ``spkg-configure.m4`` has not been written for this package;
see :issue:`27330` for more information.
