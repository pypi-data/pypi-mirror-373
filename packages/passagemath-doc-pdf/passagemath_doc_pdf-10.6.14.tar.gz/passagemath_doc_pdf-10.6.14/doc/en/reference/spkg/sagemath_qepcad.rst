.. _spkg_sagemath_qepcad:

======================================================================================================================
sagemath_qepcad: Quantifier elimination by partial cylindrical algebraic decomposition with QEPCAD
======================================================================================================================


This pip-installable source distribution ``passagemath-qepcad`` provides an interface to
`QEPCAD <https://github.com/chriswestbrown/qepcad>`_.


Example
-------

::

    $ pipx run  --pip-args="--prefer-binary" --spec "passagemath-qepcad[test]" ipython

    In [1]: from sage.all__sagemath_symbolics import *

    In [2]: var('x,y')

    In [3]: ellipse = 3*x^2 + 2*x*y + y^2 - x + y - 7

    In [4]: F = qepcad_formula.exists(y, ellipse == 0); F

    In [5]: qepcad(F)


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
- :ref:`spkg_qepcad`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_repl`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-qepcad ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
