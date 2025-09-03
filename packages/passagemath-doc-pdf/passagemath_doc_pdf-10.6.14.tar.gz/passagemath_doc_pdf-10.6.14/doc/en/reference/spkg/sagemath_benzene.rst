.. _spkg_sagemath_benzene:

=======================================================================================================
sagemath_benzene: Generate fusene and benzenoid graphs with benzene
=======================================================================================================


This pip-installable distribution ``passagemath-benzene`` provides an interface
to benzene, a program for the efficient generation of all nonisomorphic
fusenes and benzenoids with a given number of faces.


What is included
----------------

* Binary wheels on PyPI contain prebuilt copies of the benzene executable.


Examples
--------

Using the benzene program on the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-benzene[test]" sage -sh -c benzene

Finding the installation location of the benzene program::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-benzene[test]" ipython

    In [1]: from sage.features.graph_generators import Benzene

    In [2]: Benzene().absolute_filename()
    Out[2]: '.../bin/benzene'

Using the Python interface::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-benzene[test]" ipython

    In [1]: from sage.all__sagemath_benzene import *

    In [2]: len(list(graphs.fusenes(9, benzenoids=True)))
    Out[2]: 6505


Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_benzene`
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

    passagemath-benzene ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
