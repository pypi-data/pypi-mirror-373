.. _spkg_sagemath_plantri:

=======================================================================================================
sagemath_plantri: Generating planar graphs with plantri and fullgen
=======================================================================================================


This pip-installable distribution ``passagemath-plantri`` provides an interface
to `plantri <https://users.cecs.anu.edu.au/~bdm/plantri/>`_.


What is included
----------------

* Binary wheels on PyPI contain prebuilt copies of plantri executables.


Examples
--------

Using plantri programs on the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-plantri" sage -sh -c plantri


Finding the installation location of a plantri program::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-plantri[test]" ipython

    In [1]: from sage.features.graph_generators import Plantri

    In [2]: Plantri().absolute_filename()
    Out[2]: '.../bin/plantri'


Using the Python interface::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-plantri[test]" ipython

    In [1]: from sage.all__sagemath_plantri import *

    In [2]: len(list(graphs.planar_graphs(4, minimum_edges=4)))
    Out[2]: 4

    In [3]: gen = graphs.triangulations(6, only_eulerian=True); g = next(gen)

    In [4]: g.is_isomorphic(graphs.OctahedralGraph())
    Out[4]: True


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
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_plantri`
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

    passagemath-plantri ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
