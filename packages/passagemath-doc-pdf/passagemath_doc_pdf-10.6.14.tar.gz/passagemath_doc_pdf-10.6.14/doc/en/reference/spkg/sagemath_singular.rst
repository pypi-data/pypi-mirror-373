.. _spkg_sagemath_singular:

========================================================================================================================================
sagemath_singular: Computer algebra, algebraic geometry, singularity theory with Singular
========================================================================================================================================


This pip-installable distribution ``passagemath-singular``
provides interfaces to `Singular <https://www.singular.uni-kl.de/>`__,
the computer algebra system for polynomial computations, with
special emphasis on commutative and non-commutative algebra, algebraic
geometry, and singularity theory.

It also ships various modules of the Sage library that depend on Singular.


What is included
----------------

- `Cython interface to libSingular <https://passagemath.org/docs/latest/html/en/reference/libs/index.html#libsingular>`_

- `pexpect interface to Singular <https://passagemath.org/docs/latest/html/en/reference/interfaces/sage/interfaces/singular.html>`_

- various other modules, see https://github.com/passagemath/passagemath/blob/main/pkgs/sagemath-singular/MANIFEST.in

- the `PySingular <https://pypi.org/project/PySingular/>`__ API

- The binary wheels published on PyPI include a prebuilt copy of Singular.


Examples
--------

Using Singular on the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-singular" sage -singular
                         SINGULAR                                 /
     A Computer Algebra System for Polynomial Computations       /   version 4.4.0
                                                               0<
     by: W. Decker, G.-M. Greuel, G. Pfister, H. Schoenemann     \   Apr 2024
    FB Mathematik der Universitaet, D-67653 Kaiserslautern        \
    >

Finding the installation location of the Singular executable::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-singular[test]" ipython

    In [1]: from sage.features.singular import Singular

    In [2]: Singular().absolute_filename()
    Out[2]: '/Users/mkoeppe/.local/pipx/.cache/51651a517394201/lib/python3.11/site-packages/sage_wheels/bin/Singular'

Using the Cython interface to Singular::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-singular[test]" ipython

    In [1]: from sage.all__sagemath_singular import *

    In [2]: from sage.libs.singular.function import singular_function

    In [3]: P = PolynomialRing(GF(Integer(7)), names=['a', 'b', 'c', 'd'])

    In [4]: I = sage.rings.ideal.Cyclic(P)

    In [5]: std = singular_function('std')

    In [6]: std(I)
    Out[6]: [a + b + c + d, b^2 + 2*b*d + d^2, b*c^2 + c^2*d - b*d^2 - d^3,
             b*c*d^2 + c^2*d^2 - b*d^3 + c*d^3 - d^4 - 1, b*d^4 + d^5 - b - d,
             c^3*d^2 + c^2*d^3 - c - d, c^2*d^4 + b*c - b*d + c*d - 2*d^2]


Available as extras, from other distributions
---------------------------------------------

Jupyter kernel
~~~~~~~~~~~~~~

``pip install "passagemath-singular[jupyterkernel]"``
 installs the kernel for use in the Jupyter notebook and JupyterLab

``pip install "passagemath-singular[notebook]"``
 installs the kernel and the Jupyter notebook

``pip install "passagemath-singular[jupyterlab]"``
 installs the kernel and JupyterLab


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
- :ref:`spkg_memory_allocator`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_pexpect`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_flint`
- :ref:`spkg_sagemath_linbox`
- :ref:`spkg_sagemath_modules`
- :ref:`spkg_sagemath_ntl`
- :ref:`spkg_sagemath_pari`
- :ref:`spkg_setuptools`
- :ref:`spkg_singular`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-singular ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
