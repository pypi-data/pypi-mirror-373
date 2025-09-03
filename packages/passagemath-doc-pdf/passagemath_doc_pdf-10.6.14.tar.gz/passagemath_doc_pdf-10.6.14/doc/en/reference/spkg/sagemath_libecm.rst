.. _spkg_sagemath_libecm:

===============================================================================================================================
sagemath_libecm: Elliptic curve method for integer factorization using GMP-ECM
===============================================================================================================================


This pip-installable package ``passagemath-libecm`` provides
interfaces to `GMP-ECM <https://gitlab.inria.fr/zimmerma/ecm>`_, the implementation
of the Elliptic Curve Method for integer factorization.


What is included
----------------

- `Python interface to the ECM program <https://passagemath.org/docs/latest/html/en/reference/interfaces/sage/interfaces/ecm.html#module-sage.interfaces.ecm>`_

- `Cython interface to the libecm library <https://passagemath.org/docs/latest/html/en/reference/libs/sage/libs/libecm.html#module-sage.libs.libecm>`_

- The binary wheels published on PyPI include a prebuilt copy of GMP-ECM (executable and library).


Examples
--------

::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-libecm[test]" ipython

    In [1]: from sage.libs.libecm import ecmfactor

    In [2]: N = 11 * 43570062353753446053455610056679740005056966111842089407838902783209959981593077811330507328327968191581

    In [3]: ecmfactor(N, 100, verbose=True)
    Performing one curve with B1=100
    Found factor in step 1: 11
    Out[3]: (True, 11, ...)

    In [4]: ecmfactor(N//11, 100, verbose=True)
    Performing one curve with B1=100
    Found no factor.
    Out[4]: (False, None)


Available as extras, from other distributions
---------------------------------------------

``pip install passagemath-libecm[pari]`` additionally makes PARI available (for primality testing)


Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_ecm`
- :ref:`spkg_gmp`
- :ref:`spkg_iml`
- :ref:`spkg_linbox`
- :ref:`spkg_m4ri`
- :ref:`spkg_m4rie`
- :ref:`spkg_memory_allocator`
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

    passagemath-libecm ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
