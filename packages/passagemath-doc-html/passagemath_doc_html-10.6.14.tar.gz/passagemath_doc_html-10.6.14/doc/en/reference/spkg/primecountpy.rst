.. _spkg_primecountpy:

primecountpy: Cython interface for C++ primecount library
=========================================================

Description
-----------

primecountpy is a Cython interface for the C++ primecount library.

We are using the compatible fork passagemath-primesieve-primecount.

License
-------

GPLv3

Upstream Contact
----------------

https://pypi.org/project/passagemath-primesieve-primecount/



Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_primecount`

Version Information
-------------------

package-version.txt::

    0.1.1.1

version_requirements.txt::

    passagemath-primesieve-primecount

Equivalent System Packages
--------------------------

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install primecountpy

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install python3-primecountpy

.. tab:: Gentoo Linux:

   .. CODE-BLOCK:: bash

       $ sudo emerge dev-python/primecountpy


If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure`` will check if the system package can be used.
