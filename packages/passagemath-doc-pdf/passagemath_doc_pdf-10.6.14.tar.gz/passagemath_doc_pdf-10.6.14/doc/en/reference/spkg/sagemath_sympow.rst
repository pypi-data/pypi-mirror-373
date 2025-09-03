.. _spkg_sagemath_sympow:

=============================================================================================================
sagemath_sympow: Special values of symmetric power elliptic curve L-functions with sympow
=============================================================================================================


This pip-installable distribution ``passagemath-sympow`` provides an interface
to sympow.


What is included
----------------

* Binary wheels on PyPI contain prebuilt copies of the sympow executable and data files.


Examples
--------

Using the sympow program on the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-sympow" sage -sh -c sympow


Finding the installation location of the sympow executable::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-sympow[test]" ipython

    In [1]: from sage.features.lrs import LrsNash

    In [2]: LrsNash().absolute_filename()
    Out[2]: '/Users/mkoeppe/.local/pipx/.cache/db3f5a0e2996f81/lib/python3.11/site-packages/sage_wheels/bin/lrsnash'


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
- :ref:`spkg_sympow`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-sympow ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
