.. _spkg_threejs:

jupyter_threejs_sage: Sage: Open Source Mathematics Software: Jupyter extension for 3D graphics with threejs
============================================================================================================

Description
-----------

Sage: Open Source Mathematics Software: Jupyter extension for 3D graphics with threejs

License
-------

MIT License

Upstream Contact
----------------

https://pypi.org/project/jupyter-threejs-sage/



Type
----

standard


Dependencies
------------

- $(PYTHON)
- :ref:`spkg_pip`

Version Information
-------------------

package-version.txt::

    130

version_requirements.txt::

    jupyter-threejs-sage

Equivalent System Packages
--------------------------

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install threejs-sage=122.\*

# See https://repology.org/project/threejs/versions, https://repology.org/project/threejs-sage/versions

However, these system packages will not be used for building Sage
because ``spkg-configure.m4`` has not been written for this package;
see :issue:`27330` for more information.
