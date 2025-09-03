.. _spkg_sagemath_kissat:

=======================================================================================================
sagemath_kissat: Interface to the SAT solver kissat
=======================================================================================================


This pip-installable distribution ``passagemath-kissat`` provides an interface
to the SAT solver `kissat <https://fmv.jku.at/kissat/>`_, a condensed and improved
reimplementation of CaDiCaL in C.


What is included
----------------

* Binary wheels on PyPI contain prebuilt copies of the kissat executable.


Examples
--------

Using kissat programs on the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-kissat" sage -sh -c kissat

Finding the installation location of the kissat program::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-kissat[test]" ipython

    In [1]: from sage.features.sat import Kissat

    In [2]: Kissat().absolute_filename()
    Out[2]: '.../bin/kissat'

Use with `sage.sat <https://passagemath.org/docs/latest/html/en/reference/sat/index.html>`_::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-kissat[test]" ipython

    In [1]: from sage.all__sagemath_kissat import *

    In [2]: from sage.sat.solvers.dimacs import Kissat

    In [3]: solver = Kissat(); solver.add_clause((1,2)); solver.add_clause((-1,2)); solver.add_clause((1,-2))

    In [4]: solver()
    Out[4]: (None, True, True)


Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_gmp`
- :ref:`spkg_kissat`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_objects`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-kissat ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
