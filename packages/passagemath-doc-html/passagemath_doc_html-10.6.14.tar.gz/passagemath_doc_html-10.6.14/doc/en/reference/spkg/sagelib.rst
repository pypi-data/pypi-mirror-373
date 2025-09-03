.. _spkg_sagelib:

=========================================================================================
sagelib: Standard Python Library
=========================================================================================


This pip-installable distribution ``passagemath-standard`` is a metapackage
that provides all standard components of the Sage library.


Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_sagemath_standard_no_symbolics`
- :ref:`spkg_sagemath_symbolics`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-standard ~= 10.6.14.0

Equivalent System Packages
--------------------------

# See https://repology.org/project/python:sagelib/versions

If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure`` will check if the system package can be used.
