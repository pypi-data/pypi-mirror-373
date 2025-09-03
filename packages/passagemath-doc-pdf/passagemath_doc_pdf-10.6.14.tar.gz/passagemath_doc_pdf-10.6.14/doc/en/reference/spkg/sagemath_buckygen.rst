.. _spkg_sagemath_buckygen:

=======================================================================================================
sagemath_buckygen: Generation of nonisomorphic fullerenes with buckygen
=======================================================================================================


This pip-installable distribution ``passagemath-buckygen`` provides an interface
to `buckygen <http://caagt.ugent.be/buckygen/>`_, a program for the efficient
generation of all nonisomorphic fullerenes.


What is included
----------------

* Binary wheels on PyPI contain prebuilt copies of buckygen.


Examples
--------

Using the buckygen program on the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-buckygen[test]" sage -sh -c buckygen

Finding the installation location of the buckygen program::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-buckygen[test]" ipython

    In [1]: from sage.features.graph_generators import Buckygen

    In [2]: Buckygen().absolute_filename()
    Out[2]: '.../bin/buckygen'

Using the Python interface::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-buckygen[test]" ipython

    In [1]: from sage.all__sagemath_buckygen import *

    In [2]: len(list(graphs.fullerenes(60)))
    Out[2]: 1812

    In [3]: gen = graphs.fullerenes(60, ipr=True); next(gen)
    Out[3]: Graph on 60 vertices


Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_buckygen`
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_gmp`
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

    passagemath-buckygen ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
