.. _spkg_sagemath_planarity:

================================================================================================
sagemath_planarity: Graph planarity with the edge addition planarity suite
================================================================================================


This pip-installable distribution ``passagemath-planarity`` is a small
optional distribution for use with ``passagemath-graphs``.

It provides a Cython interface to the
`Edge Addition Planarity Suite <https://github.com/graph-algorithms/edge-addition-planarity-suite/>`_
by John Boyer.


What is included
----------------

- `Cython interface to Boyer's planarity algorithm <https://passagemath.org/docs/latest/html/en/reference/graphs/sage/graphs/planarity.html>`_


Examples
--------

::

    $ pipx run --pip-args="--prefer-binary" --spec "passagemath-planarity[test]" ipython

    In [1]: from sage.all__sagemath_planarity import *

    In [2]: g = graphs.PetersenGraph()

    In [3]: g.is_planar()
    Out[3]: False


Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_boost_cropped`
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_pkgconf`
- :ref:`spkg_pkgconfig`
- :ref:`spkg_planarity`
- :ref:`spkg_sage_conf`
- :ref:`spkg_sage_setup`
- :ref:`spkg_sagemath_environment`
- :ref:`spkg_setuptools`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-planarity ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
