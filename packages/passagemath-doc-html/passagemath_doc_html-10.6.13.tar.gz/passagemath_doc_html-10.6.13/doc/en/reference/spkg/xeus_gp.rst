.. _spkg_xeus_gp:

xeus_gp: Jupyter kernel for PARI/GP based on xeus
=================================================

Description
-----------

A Xeus-based Jupyter kernel for PARI/GP


License
-------

GPL 2 or later


Upstream Contact
----------------

- https://pari.math.u-bordeaux.fr/download.html#xeus-gp
- https://pari.math.u-bordeaux.fr/pub/pari/XEUS-GP
- https://pari.math.u-bordeaux.fr/git/xeus-gp.git
- https://github.com/passagemath/upstream-xeus-gp.git


Type
----

optional


Dependencies
------------

- :ref:`spkg_cmake`
- :ref:`spkg_ninja_build`
- :ref:`spkg_nlohmann_json`
- :ref:`spkg_pari`
- :ref:`spkg_xeus`
- :ref:`spkg_xeus_zmq`

Version Information
-------------------

package-version.txt::

    0.1.0

Equivalent System Packages
--------------------------

.. tab:: Debian/Ubuntu:

   .. CODE-BLOCK:: bash

       $ sudo apt-get install xeus-gp


However, these system packages will not be used for building Sage
because ``spkg-configure.m4`` has not been written for this package;
see :issue:`27330` for more information.
