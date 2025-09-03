.. _spkg_sagemath_cmr:

==================================================================================================
sagemath_cmr: Combinatorial matrix recognition
==================================================================================================


This pip-installable distribution ``passagemath-cmr`` is a small
optional distribution for use with `passagemath-modules <https://pypi.org/project/passagemath-modules/>`_ and
`passagemath-graphs <https://pypi.org/project/passagemath-graphs/>`_.

It provides a Cython interface to the
`CMR library <https://github.com/discopt/cmr>`_,
which implements recognition and decomposition algorithms for:

- Totally Unimodular Matrices
- Network Matrices
- Complementary Totally Unimodular Matrices
- (Strongly) Equimodular and Unimodular Matrices
- Regular Matroids
- Graphic / Cographic / Planar Matrices
- Series-Parallel Matroids


Examples
--------

::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-cmr[test]" ipython

    In [1]: from sage.all__sagemath_cmr import *

    In [2]: from sage.matrix.matrix_cmr_sparse import Matrix_cmr_chr_sparse

    In [3]: M = Matrix_cmr_chr_sparse(MatrixSpace(ZZ, 3, 3, sparse=True), [[1, 0, 1], [0, 1, 1], [1, 2, 3]]); M
    Out[3]:
    [1 0 1]
    [0 1 1]
    [1 2 3]

    In [4]: M.is_unimodular()
    Out[4]: True

    In [5]: M.is_strongly_unimodular()
    Out[5]: False


Development
-----------

::

    $ git clone --origin passagemath https://github.com/passagemath/passagemath.git  # or use your fork
    $ cd passagemath
    passagemath $ ./bootstrap
    passagemath $ source ./.homebrew-build-env         # on macOS when homebrew is in use
    passagemath $ export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/wsl/lib  # on WSL
    passagemath $ export PIP_CONSTRAINT="$(pwd)/constraints_cmr.txt"
    passagemath $ echo "passagemath-categories @ file://$(pwd)/pkgs/sagemath-categories" >> constraints_cmr.txt
    passagemath $ echo "passagemath-modules @ file://$(pwd)/pkgs/sagemath-modules" >> constraints_cmr.txt
    passagemath $ python3 -m venv cmr-venv
    passagemath $ source cmr-venv/bin/activate
    (cmr-venv) passagemath $ pip install -v -e pkgs/sagemath-cmr        \
                                            -e pkgs/sagemath-modules    \
                                            -e pkgs/sagemath-categories

Modularized use::

    (cmr-venv) passagemath $ pip install -v passagemath-repl
    (cmr-venv) passagemath $ sage
    ... sage.all is not available ...
    sage: from sage.all__sagemath_modules import *
    sage: matroids.Uniform(3, 4)
    U(3, 4): Matroid of rank 3 on 4 elements with circuit-closures
    {3: {{0, 1, 2, 3}}}

In plain Python::

    (cmr-venv) passagemath $ python3
    >>> from sage.all__sagemath_modules import *
    >>> matroids.Uniform(3, 4)
    U(3, 4): Matroid of rank 3 on 4 elements with circuit-closures
    {3: {{0, 1, 2, 3}}}

For full functionality of Sage::

    (cmr-venv) passagemath $ pip install -v passagemath-standard
    (cmr-venv) passagemath $ sage
    sage: matroids.Uniform(3, 4)
    U(3, 4): Matroid of rank 3 on 4 elements with circuit-closures
    {3: {{0, 1, 2, 3}}}


Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cmr`
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_graphs`
- :ref:`spkg_sagemath_modules`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-cmr ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
