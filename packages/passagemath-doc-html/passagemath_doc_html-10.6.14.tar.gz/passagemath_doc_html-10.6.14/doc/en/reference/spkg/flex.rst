.. _spkg_flex:

flex: Lexical analyzer generator
================================

Description
-----------

This dummy package represents GNU flex.

We do not have an SPKG for it. The purpose of this dummy package is to
associate system package lists with it.


Type
----

standard


Dependencies
------------



Version Information
-------------------



Equivalent System Packages
--------------------------

.. tab:: Alpine:

   .. CODE-BLOCK:: bash

       $ apk add flex

.. tab:: Arch Linux:

   .. CODE-BLOCK:: bash

       $ sudo pacman -S flex

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install flex

.. tab:: Debian/Ubuntu:

   .. CODE-BLOCK:: bash

       $ sudo apt-get install flex

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install flex

.. tab:: FreeBSD:

   .. CODE-BLOCK:: bash

       $ sudo pkg install flex

.. tab:: Gentoo Linux:

   .. CODE-BLOCK:: bash

       $ sudo emerge sys-devel/flex

.. tab:: Homebrew:

   .. CODE-BLOCK:: bash

       $ brew install flex

.. tab:: Nixpkgs:

   .. CODE-BLOCK:: bash

       $ nix-env -f \'\<nixpkgs\>\' --install --attr flex

.. tab:: openSUSE:

   .. CODE-BLOCK:: bash

       $ sudo zypper install flex

.. tab:: Slackware:

   .. CODE-BLOCK:: bash

       $ sudo slackpkg install flex

.. tab:: Void Linux:

   .. CODE-BLOCK:: bash

       $ sudo xbps-install flex


If the system package is installed, ``./configure`` will check if it can be used.
