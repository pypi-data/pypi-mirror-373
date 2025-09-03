.. _spkg_sagemath_sirocco:

==========================================================================================================
sagemath_sirocco: Certified root continuation with sirocco
==========================================================================================================


This pip-installable distribution ``passagemath-sirocco`` provides a Cython interface
to the `sirocco <https://github.com/miguelmarco/SIROCCO2>`_ library for computing
topologically certified root continuation of bivariate polynomials.


What is included
----------------

* `sage.libs.sirocco <https://github.com/passagemath/passagemath/blob/main/src/sage/libs/sirocco.pyx>`_


Examples
--------

::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-sirocco[test]" ipython

    In [1]: from sage.all__sagemath_sirocco import *

    In [2]: from sage.libs.sirocco import contpath

    In [3]: pol = list(map(RR,[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))

    In [4]: contpath(2, pol, RR(0), RR(0))
    Out[4]:
    [(0.0, 0.0, 0.0),
     (0.3535533905932738, -0.12500000000000003, 0.0),
     (0.7071067811865476, -0.5000000000000001, 0.0),
     (1.0, -1.0, 0.0)]


Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_modules`
- :ref:`spkg_setuptools`
- :ref:`spkg_sirocco`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-sirocco ~= 10.6.14.0

Equivalent System Packages
--------------------------

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install sagemath-sirocco


However, these system packages will not be used for building Sage
because ``spkg-configure.m4`` has not been written for this package;
see :issue:`27330` for more information.
