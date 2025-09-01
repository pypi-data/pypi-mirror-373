.. _spkg_playwright:

playwright: High-level API to automate web browsers
===================================================

Description
-----------

High-level API to automate web browsers

SageMath uses Playwright to take screenshots of 3D graphics in a headless browser.
Exporting Jupyter notebooks to PDF via nbconvert's WebPDF technology also uses Playwright.

License
-------

Apache-2.0

Upstream Contact
----------------

https://pypi.org/project/playwright/



Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_typing_extensions`

Version Information
-------------------

requirements.txt::

    playwright

Equivalent System Packages
--------------------------

.. tab:: Arch Linux:

   .. CODE-BLOCK:: bash

       $ sudo pacman -S python-playwright

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install playwright

.. tab:: Nixpkgs:

   .. CODE-BLOCK:: bash

       $ nix-env -f \'\<nixpkgs\>\' --install --attr python3.\$\{PYTHON_MINOR\}-playwright

# See https://repology.org/project/python:playwright/versions

However, these system packages will not be used for building Sage
because ``spkg-configure.m4`` has not been written for this package;
see :issue:`27330` for more information.
