.. _spkg_libuuid:

libuuid: Universally Unique Identifier library
==============================================

Description
-----------

API for the generation of Universally Unique Identifiers (UUID).


Upstream Contact
----------------

http://www.ossp.org/pkg/lib/uuid/


Type
----

optional


Dependencies
------------



Version Information
-------------------



Equivalent System Packages
--------------------------

.. tab:: Alpine:

   .. CODE-BLOCK:: bash

       $ apk add libuuid util-linux-dev

.. tab:: Arch Linux:

   .. CODE-BLOCK:: bash

       $ sudo pacman -S util-linux-libs

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install libuuid

.. tab:: Debian/Ubuntu:

   .. CODE-BLOCK:: bash

       $ sudo apt-get install uuid-dev

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install libuuid-devel


If the system package is installed, ``./configure`` will check if it can be used.
