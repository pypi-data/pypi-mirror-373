.. _spkg_sagemath_pari:

==========================================================================================================
sagemath_pari: Computational Number Theory with PARI/GP
==========================================================================================================


This pip-installable distribution ``passagemath-pari`` is a small
distribution that provides modules that depend on
`PARI/GP <https://pari.math.u-bordeaux.fr/>`__, the computer algebra
system designed for fast computations in number theory: factorizations,
algebraic number theory, elliptic curves, modular forms, L-functions...


What is included
----------------

- `integer factorization <https://passagemath.org/docs/10.6/html/en/reference/rings_standard/sage/rings/factorint_pari.html#module-sage.rings.factorint_pari>`__

- `finite fields <https://passagemath.org/docs/10.6/html/en/reference/finite_rings/sage/rings/finite_rings/finite_field_pari_ffelt.html#module-sage.rings.finite_rings.finite_field_pari_ffelt>`__

- much of the `p-adics functionality of the Sage library <https://passagemath.org/docs/10.6/html/en/reference/padics/index.html>`__

- `discrete valuations <https://passagemath.org/docs/10.6/html/en/reference/valuations/index.html>`__

- parts of the `quadratic forms functionality of the Sage library <https://passagemath.org/docs/10.6/html/en/reference/quadratic_forms/index.html>`__

- various other modules with dependencies on PARI/GP, see `MANIFEST <https://github.com/passagemath/passagemath/blob/main/pkgs/sagemath-pari/MANIFEST.in>`_

- the `cypari2 <https://pypi.org/project/cypari2/>`_ API

- the `pari-jupyter kernel <https://github.com/passagemath/upstream-pari-jupyter>`__

- the binary wheels on PyPI ship a prebuilt copy of PARI/GP

- the binary wheels on PyPI ship XEUS-GP, another Jupyter kernel for PARI/GP


Examples
--------

Starting the GP calculator from the command line::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-pari" sage -gp
    GP/PARI CALCULATOR Version 2.17.2 (released)
    ...

Using the pexpect interface to the GP calculator::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-pari[test]" ipython

    In [1]: from sage.interfaces.gp import gp

    In [2]: E = gp.ellinit([1,2,3,4,5])

    In [3]: E.ellglobalred()
    Out[3]: [10351, [1, -1, 0, -1], 1, [11, 1; 941, 1], [[1, 5, 0, 1], [1, 5, 0, 1]]]

Using the ``cypari2`` library interface::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-pari" python

    >>> import cypari2
    >>> pari = cypari2.Pari()

    >>> pari(2).zeta()
    1.64493406684823

    >>> p = pari("x^3 + x^2 + x - 1")
    >>> modulus = pari("t^3 + t^2 + t - 1")
    >>> fq = p.factorff(3, modulus)
    >>> fq.lift().centerlift()
    [x - t, 1; x + (t^2 + t - 1), 1; x + (-t^2 - 1), 1]


Available as extras, from other distributions
---------------------------------------------

PARI/GP data packages
~~~~~~~~~~~~~~~~~~~~~

See https://pari.math.u-bordeaux.fr/packages.html for detailed descriptions.

``pip install "passagemath-pari[elldata]"``

``pip install "passagemath-pari[galdata]"``

``pip install "passagemath-pari[galpol]"``

``pip install "passagemath-pari[nflistdata]"``

``pip install "passagemath-pari[nftables]"``

``pip install "passagemath-pari[seadata]"``

``pip install "passagemath-pari[seadata-big]"``

``pip install "passagemath-pari[seadata-small]"``


Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_conway_polynomials`
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_givaro`
- :ref:`spkg_gmp`
- :ref:`spkg_memory_allocator`
- :ref:`spkg_mpc`
- :ref:`spkg_mpfr`
- :ref:`spkg_mpmath`
- :ref:`spkg_pari`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_categories`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_sagemath_flint`
- :ref:`spkg_sagemath_modules`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-pari ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
