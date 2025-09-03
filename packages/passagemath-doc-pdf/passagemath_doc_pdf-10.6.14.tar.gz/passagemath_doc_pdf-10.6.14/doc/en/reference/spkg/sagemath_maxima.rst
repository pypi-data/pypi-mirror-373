.. _spkg_sagemath_maxima:

===================================================================================
sagemath_maxima: Symbolic calculus with maxima
===================================================================================


This pip-installable distribution ``passagemath-maxima`` provides
interfaces to `Maxima <https://passagemath.org/docs/latest/html/en/reference/spkg/maxima.html>`_.


What is included
----------------

* Binary wheels on PyPI contain prebuilt copies of `Maxima <https://passagemath.org/docs/latest/html/en/reference/spkg/maxima.html>`_.


Examples
--------

Starting Maxima from the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-maxima" sage -maxima

Using the pexpect interface to Maxima::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-maxima[test]" ipython

    In [1]: from sage.interfaces.maxima import maxima

    In [2]: maxima('1+1')
    Out[2]: 2

Using the library interface to Maxima::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-maxima[test]" ipython

    In [1]: from sage.interfaces.maxima_lib import maxima_lib

    In [2]: F = maxima_lib('x^5 - y^5').factor()

    In [3]: F.display2d()
    Out[3]:
                               4      3    2  2    3      4
                   - (y - x) (y  + x y  + x  y  + x  y + x )


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
- :ref:`spkg_maxima`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_ecl`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_setuptools`
- :ref:`spkg_singular`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-maxima ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
