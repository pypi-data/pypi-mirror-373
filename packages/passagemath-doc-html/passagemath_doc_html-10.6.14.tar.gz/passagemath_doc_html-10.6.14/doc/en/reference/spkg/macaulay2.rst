.. _spkg_macaulay2:

macaulay2: System for computing in commutative algebra, algebraic geometry and related fields
=============================================================================================

Description
-----------

Macaulay2 is a system for computing in commutative algebra, algebraic geometry and related fields.


License
-------

GPL v2 or v3, see https://github.com/Macaulay2/M2/blob/master/M2/INSTALL


Upstream Contact
----------------

https://github.com/Macaulay2/M2


Type
----

optional


Dependencies
------------

- $(BLAS)
- $(MP_LIBRARY)
- $(PYTHON)
- :ref:`spkg_4ti2`
- :ref:`spkg_boost_cropped`
- :ref:`spkg_cddlib`
- :ref:`spkg_cmake`
- :ref:`spkg_eigen`
- :ref:`spkg_fflas_ffpack`
- :ref:`spkg_flint`
- :ref:`spkg_frobby`
- :ref:`spkg_gc`
- :ref:`spkg_gdbm`
- :ref:`spkg_gfan`
- :ref:`spkg_gfortran`
- :ref:`spkg_git`
- :ref:`spkg_givaro`
- :ref:`spkg_glpk`
- :ref:`spkg_googletest`
- :ref:`spkg_libffi`
- :ref:`spkg_liblzma`
- :ref:`spkg_libnauty`
- :ref:`spkg_libxml2`
- :ref:`spkg_lrslib`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfi`
- :ref:`spkg_mpfr`
- :ref:`spkg_mpsolve`
- :ref:`spkg_msolve`
- :ref:`spkg_nauty`
- :ref:`spkg_ncurses`
- :ref:`spkg_ninja_build`
- :ref:`spkg_normaliz`
- :ref:`spkg_ntl`
- :ref:`spkg_onetbb`
- :ref:`spkg_pkgconf`
- :ref:`spkg_readline`
- :ref:`spkg_singular`
- :ref:`spkg_topcom`
- :ref:`spkg_zlib`

Version Information
-------------------

package-version.txt::

    1.25.06

Equivalent System Packages
--------------------------

.. tab:: Debian/Ubuntu:

   .. CODE-BLOCK:: bash

       $ sudo apt-get install macaulay2

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install Macaulay2

.. tab:: Homebrew:

   .. CODE-BLOCK:: bash

       $ brew install macaulay2/tap/M2


However, these system packages will not be used for building Sage
because ``spkg-configure.m4`` has not been written for this package;
see :issue:`27330` for more information.
