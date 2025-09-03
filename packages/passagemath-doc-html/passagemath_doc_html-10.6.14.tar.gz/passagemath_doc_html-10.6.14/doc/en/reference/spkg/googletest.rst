.. _spkg_googletest:

googletest: Google testing and mocking framework
================================================

Description
-----------

C++ test framework


License
-------

BSD-3-Clause license


Upstream Contact
----------------

https://github.com/google/googletest


Type
----

optional


Dependencies
------------

- :ref:`spkg_cmake`
- :ref:`spkg_ninja_build`

Version Information
-------------------

package-version.txt::

    1.16.0

Equivalent System Packages
--------------------------

.. tab:: Alpine:

   .. CODE-BLOCK:: bash

       $ apk add gtest-dev

.. tab:: Arch Linux:

   .. CODE-BLOCK:: bash

       $ sudo pacman -S gtest

.. tab:: Debian/Ubuntu:

   .. CODE-BLOCK:: bash

       $ sudo apt-get install googletest

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install gtest

.. tab:: FreeBSD:

   .. CODE-BLOCK:: bash

       $ sudo pkg install devel/googletest

.. tab:: Gentoo Linux:

   .. CODE-BLOCK:: bash

       $ sudo emerge dev-cpp/gtest

.. tab:: Homebrew:

   .. CODE-BLOCK:: bash

       $ brew install googletest

.. tab:: Nixpkgs:

   .. CODE-BLOCK:: bash

       $ nix-env -f \'\<nixpkgs\>\' --install --attr gtest

.. tab:: openSUSE:

   .. CODE-BLOCK:: bash

       $ sudo zypper install googletest

.. tab:: Void Linux:

   .. CODE-BLOCK:: bash

       $ sudo xbps-install gtest-devel

# See https://repology.org/project/gtest/versions

If the system package is installed, ``./configure`` will check if it can be used.
