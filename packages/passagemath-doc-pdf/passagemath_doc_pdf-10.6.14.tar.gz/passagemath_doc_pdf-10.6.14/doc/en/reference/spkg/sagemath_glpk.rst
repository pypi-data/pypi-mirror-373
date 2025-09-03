.. _spkg_sagemath_glpk:

=================================================================================================================================
sagemath_glpk: Linear and mixed integer linear optimization backend using GLPK
=================================================================================================================================


This pip-installable distribution ``passagemath-glpk`` provides
a backend for linear and mixed integer linear optimization backend using GLPK.

It can be installed as an extra of the distribution
`sagemath-polyhedra <https://pypi.org/project/sagemath-polyhedra>`_::

  $ pip install "passagemath-polyhedra[glpk]"


What is included
----------------

* `GLPK backends <https://passagemath.org/docs/latest/html/en/reference/numerical/index.html#linear-optimization-lp-and-mixed-integer-linear-optimization-mip-solver-backends>`_ for LP, MILP, and graphs


Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_glpk`
- :ref:`spkg_gmp`
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

    passagemath-glpk ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
