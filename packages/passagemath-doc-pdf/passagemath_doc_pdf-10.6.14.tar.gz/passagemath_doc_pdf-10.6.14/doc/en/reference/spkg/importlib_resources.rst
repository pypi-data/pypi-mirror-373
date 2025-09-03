.. _spkg_importlib_resources:

importlib_resources: Read resources from Python packages
========================================================

Description
-----------

Read resources from Python packages

License
-------

Apache2

Upstream Contact
----------------

https://pypi.org/project/importlib-resources/



Type
----

standard


Dependencies
------------

- $(PYTHON)
- :ref:`spkg_pip`
- :ref:`spkg_zipp`

Version Information
-------------------

package-version.txt::

    6.5.2

src/pyproject.toml::

    importlib_resources >= 5.12; python_version<'3.12'

version_requirements.txt::

    importlib_resources

Equivalent System Packages
--------------------------

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install importlib-resources

.. tab:: Debian/Ubuntu:

   .. CODE-BLOCK:: bash

       $ sudo apt-get install python3-importlib-resources


If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure`` will check if the system package can be used.
