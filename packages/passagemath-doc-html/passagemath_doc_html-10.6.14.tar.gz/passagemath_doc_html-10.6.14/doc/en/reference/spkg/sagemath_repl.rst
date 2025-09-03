.. _spkg_sagemath_repl:

===========================================================================================================
sagemath_repl: IPython kernel, Sage preparser, doctester
===========================================================================================================


The pip-installable distribution ``passagemath-repl`` is a
distribution of a small part of the Sage Library.

It provides a small, fundamental subset of the modules of the Sage library
("sagelib", ``passagemath-standard``), providing the IPython kernel, Sage preparser,
and doctester.


What is included
----------------

* `Doctesting Framework <https://passagemath.org/docs/latest/html/en/reference/doctest/index.html>`_

* `The Sage REPL <https://passagemath.org/docs/latest/html/en/reference/repl/sage/repl/index.html>`_


Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_ipykernel`
- :ref:`spkg_ipython`
- :ref:`spkg_ipywidgets`
- :ref:`spkg_jupyter_client`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_objects`
- :ref:`spkg_setuptools`
- :ref:`spkg_typing_extensions`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-repl ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
