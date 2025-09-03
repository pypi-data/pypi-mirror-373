.. _spkg_sagemath_plot:

=======================================================================================================================
sagemath_plot: Plotting and graphics with Matplotlib, Three.JS, etc.
=======================================================================================================================


This pip-installable distribution ``passagemath-plot`` is a distribution of a part of the Sage Library.

It provides the namespace packages ``sage.plot`` and ``sage.plot.plot3d``, which provide functions for plotting that are very similar to Mathematica's plotting functions.  This is analogous to how matplotlib's ``pyplot`` package provides a UI on top of the core ``matplotlib`` library that is similar to matlab's plotting UI.

What is included
----------------

* `2D Graphics <https://passagemath.org/docs/latest/html/en/reference/plotting/index.html>`_

* Backend for 2D graphics: `matplotlib <https://passagemath.org/docs/latest/html/en/reference/spkg/matplotlib.html>`_

* `3D Graphics <https://passagemath.org/docs/latest/html/en/reference/plot3d/index.html>`_

* Backend for 3D graphics: `three.js <https://passagemath.org/docs/latest/html/en/reference/spkg/threejs.html>`_

* Interfaces: `Gnuplot <https://passagemath.org/docs/latest/html/en/reference/interfaces/sage/interfaces/gnuplot.html>`_, `Jmol <https://passagemath.org/docs/latest/html/en/reference/interfaces/sage/interfaces/jmoldata.html>`_, `POV-Ray <https://passagemath.org/docs/latest/html/en/reference/interfaces/sage/interfaces/povray.html>`_, `Tachyon <https://passagemath.org/docs/latest/html/en/reference/interfaces/sage/interfaces/tachyon.html>`_

Examples
--------

::

   $ pipx run --pip-args="--prefer-binary" --spec "passagemath-plot[test]" ipython

   In [1]: from sage.all__sagemath_plot import *

   In [2]: scatter_plot([[0,1],[2,2],[4.3,1.1]], marker='s').save('output.png')

   In [3]: G = tetrahedron((0,-3.5,0), color='blue') + cube((0,-2,0), color=(.25,0,.5))

   In [4]: G.show(aspect_ratio=[1,1,1])
   Graphics3d Object

Available as extras, from other distributions
---------------------------------------------

``pip install "passagemath-plot[graphs]"``
 Graphs and networks: `sagemath-graphs <https://pypi.org/project/passagemath-graphs/>`_

``pip install "passagemath-plot[jsmol]"``
 Alternative backend for 3D graphics: `jupyter-jsmol <https://passagemath.org/docs/latest/html/en/reference/spkg/jupyter_jsmol.html>`_

``pip install "passagemath-plot[playwright]"``
 Screenshotting tool for saving 3D graphics as 2D image files: `playwright <https://pypi.org/project/playwright/>`_

``pip install "passagemath-plot[polyhedra]"``
 Polyhedra in arbitrary dimension, plotting in dimensions 2, 3, 4: `passagemath-polyhedra <https://pypi.org/project/passagemath-polyhedra/>`_

``pip install "passagemath-plot[symbolics]"``
 Defining and plotting symbolic functions and manifolds: `passagemath-symbolics <https://pypi.org/project/passagemath-symbolics/>`_

``pip install "passagemath-plot[tachyon]"``
 Ray tracing system, needed for saving 3D graphics as 2D image files:
 `passagemath-tachyon <https://pypi.org/project/passagemath-tachyon/>`_


Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_gmp`
- :ref:`spkg_gmpy2`
- :ref:`spkg_matplotlib`
- :ref:`spkg_memory_allocator`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_numpy`
- :ref:`spkg_pillow`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_modules`
- :ref:`spkg_scipy`
- :ref:`spkg_setuptools`
- :ref:`spkg_threejs`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-plot ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
