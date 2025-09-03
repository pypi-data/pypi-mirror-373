.. _spkg_sagemath_ntl:

======================================================================================================
sagemath_ntl: Computational Number Theory with NTL
======================================================================================================


This pip-installable package ``passagemath-ntl`` is a small
distribution that provides modules that depend on
`NTL <https://libntl.org/>`_, the library for doing number theory.


What is included
----------------

* Computation of Bernoulli numbers modulo p:

  * `Cython wrapper for bernmm library <https://passagemath.org/docs/latest/html/en/reference/rings_standard/sage/rings/bernmm.html>`_
  * `Bernoulli numbers modulo p <https://passagemath.org/docs/latest/html/en/reference/rings_standard/sage/rings/bernoulli_mod_p.html>`_

* Finite fields of characteristic 2

  * `Finite fields of characteristic 2 <https://passagemath.org/docs/latest/html/en/reference/finite_rings/sage/rings/finite_rings/finite_field_ntl_gf2e.html>`_
  * `Elements of finite fields of characteristic 2 <https://passagemath.org/docs/latest/html/en/reference/finite_rings/sage/rings/finite_rings/element_ntl_gf2e.html>`_

* p-adic extension elements:

  * `p-adic Extension Element <https://passagemath.org/docs/latest/html/en/reference/padics/sage/rings/padics/padic_ext_element.html#module-sage.rings.padics.padic_ext_element>`_
  * `p-adic ZZ_pX Element <https://passagemath.org/docs/latest/html/en/reference/padics/sage/rings/padics/padic_ZZ_pX_element.html>`_
  * `p-adic ZZ_pX CR Element <https://passagemath.org/docs/latest/html/en/reference/padics/sage/rings/padics/padic_ZZ_pX_CR_element.html>`_
  * `p-adic ZZ_pX CA Element <https://passagemath.org/docs/latest/html/en/reference/padics/sage/rings/padics/padic_ZZ_pX_CA_element.html>`_
  * `p-adic ZZ_pX FM Element <https://passagemath.org/docs/latest/html/en/reference/padics/sage/rings/padics/padic_ZZ_pX_FM_element.html>`_
  * `PowComputer_ext <https://passagemath.org/docs/latest/html/en/reference/padics/sage/rings/padics/pow_computer_ext.html>`_

* `Frobenius on Monsky-Washnitzer cohomology of a hyperelliptic curve <https://passagemath.org/docs/latest/html/en/reference/arithmetic_curves/sage/schemes/hyperelliptic_curves/hypellfrob.html>`_

* see `MANIFEST <https://github.com/passagemath/passagemath/blob/main/pkgs/sagemath-ntl/MANIFEST.in>`_


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
- :ref:`spkg_m4ri`
- :ref:`spkg_memory_allocator`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfi`
- :ref:`spkg_mpfr`
- :ref:`spkg_ntl`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_modules`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-ntl ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
