.. _spkg_pplite:

pplite: Convex polyhedra library
================================

Description
-----------

PPLite is an open-source C++ library implementing the abstract domain
of convex polyhedra.

While being derived from the PPL (Parma Polyhedra Library), PPLite has
a very different goal: to provide researchers and students with a
lighter framework for experimenting with new ideas and algorithms in
the context of polyhedral computations.

License
-------

GPL 3

Upstream Contact
----------------

https://github.com/ezaffanella/PPLite


Type
----

optional


Dependencies
------------

- $(MP_LIBRARY)
- :ref:`spkg_flint`
- :ref:`spkg_mpfr`

Version Information
-------------------

package-version.txt::

    0.12

Equivalent System Packages
--------------------------

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install pplite

.. tab:: Nixpkgs:

   .. CODE-BLOCK:: bash

       $ nix-env -f \'\<nixpkgs\>\' --install --attr pplite

.. tab:: openSUSE:

   .. CODE-BLOCK:: bash

       $ sudo zypper install pplite


However, these system packages will not be used for building Sage
because ``spkg-configure.m4`` has not been written for this package;
see :issue:`27330` for more information.
