.. _spkg_sagemath_ecl:

===================================================================================
sagemath_ecl: Embeddable Common Lisp
===================================================================================


This pip-installable distribution ``passagemath-ecl`` is a distribution of a part of the Sage Library.
It ships the Python and Cython interfaces to Embeddable Common Lisp.


What is included
----------------

* `pexpect interface to Lisp <https://passagemath.org/docs/10.6/html/en/reference/interfaces/sage/interfaces/lisp.html>`__

* `Library (Cython) interface to Embeddable Common Lisp <https://passagemath.org/docs/10.6/html/en/reference/libs/sage/libs/ecl.html#module-sage.libs.ecl>`__

* Binary wheels on PyPI contain a prebuilt copy of
  `Embeddable Common Lisp <https://passagemath.org/docs/latest/html/en/reference/spkg/ecl.html>`_


Examples
--------

Starting ECL from the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-ecl[test]" sage --ecl

    ECL (Embeddable Common-Lisp) 23.9.9 (git:UNKNOWN)
    Copyright (C) 1984 Taiichi Yuasa and Masami Hagiya
    ...
    >

Finding the installation location of ECL in Python::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-ecl[test]" ipython

    In [1]: from sage.features.ecl import Ecl

    In [2]: Ecl().absolute_filename()
    Out[2]: '.../bin/ecl'

Using the Cython interface to ECL::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-ecl[test]" sage

    sage: from sage.libs.ecl import *
    sage: ecl_eval("(defun fibo (n) (cond ((= n 0) 0) ((= n 1) 1) (t (+ (fibo (- n 1)) (fibo (- n 2))))))")
    <ECL: FIBO>
    sage: ecl_eval("(mapcar 'fibo '(1 2 3 4 5 6 7))")
    <ECL: (1 1 2 3 5 8 13)>
    sage: list(_)
    [<ECL: 1>, <ECL: 1>, <ECL: 2>, <ECL: 3>, <ECL: 5>, <ECL: 8>, <ECL: 13>]


Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_ecl`
- :ref:`spkg_gmp`
- :ref:`spkg_gsl`
- :ref:`spkg_maxima`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_setuptools`
- :ref:`spkg_singular`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-ecl ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
