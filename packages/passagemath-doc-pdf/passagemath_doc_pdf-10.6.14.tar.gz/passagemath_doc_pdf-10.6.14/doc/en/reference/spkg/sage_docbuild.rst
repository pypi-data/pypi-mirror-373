.. _spkg_sage_docbuild:

========================================================================================================
sage_docbuild: Build system of the Sage documentation
========================================================================================================


This is the build system of the Sage documentation, based on Sphinx.


Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_sagelib`
- :ref:`spkg_setuptools`
- :ref:`spkg_sphinx`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-docbuild ~= 10.6.14.0

Equivalent System Packages
--------------------------

# See https://repology.org/project/sage-docbuild/versions, https://repology.org/project/python:sage-docbuild/versions

However, these system packages will not be used for building Sage
because ``spkg-configure.m4`` has not been written for this package;
see :issue:`27330` for more information.
