.. _spkg_sagemath_environment:

=================================================================================================
sagemath_environment: System and software environment
=================================================================================================


The pip-installable distribution package ``passagemath-environment`` is a
distribution of a small part of the Sage Library.

It provides a small, fundamental subset of the modules of the Sage
library ("sagelib", ``passagemath-standard``), providing the connection to the
system and software environment.


What is included
----------------

* ``sage`` script for launching the Sage REPL and accessing various developer tools
  (see ``sage --help``, `Invoking Sage <https://passagemath.org/docs/latest/html/en/reference/repl/options.html>`_).

* sage.env

* `sage.features <https://passagemath.org/docs/latest/html/en/reference/misc/sage/features.html>`_: Testing for features of the environment at runtime

* `sage.misc.package <https://passagemath.org/docs/latest/html/en/reference/misc/sage/misc/package.html>`_: Listing packages of the Sage distribution

* `sage.misc.package_dir <https://passagemath.org/docs/latest/html/en/reference/misc/sage/misc/package_dir.html>`_

* `sage.misc.temporary_file <https://passagemath.org/docs/latest/html/en/reference/misc/sage/misc/temporary_file.html>`_

* `sage.misc.viewer <https://passagemath.org/docs/latest/html/en/reference/misc/sage/misc/viewer.html>`_


Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_packaging`
- :ref:`spkg_platformdirs`
- :ref:`spkg_setuptools`
- :ref:`spkg_wheel`

Version Information
-------------------

package-version.txt::

    10.6.14

version_requirements.txt::

    passagemath-environment ~= 10.6.14.0

Equivalent System Packages
--------------------------

(none known)
