.. _spkg_jsonschema:

jsonschema: Implementation of JSON Schema validation for Python
===============================================================

Description
-----------

Implementation of JSON Schema validation for Python

License
-------

MIT

Upstream Contact
----------------

https://pypi.org/project/jsonschema/



Type
----

standard


Dependencies
------------

- $(PYTHON)
- :ref:`spkg_attrs`
- :ref:`spkg_jsonschema_specifications`
- :ref:`spkg_pip`
- :ref:`spkg_referencing`
- :ref:`spkg_rpds_py`

Version Information
-------------------

package-version.txt::

    4.22.0

version_requirements.txt::

    jsonschema

Equivalent System Packages
--------------------------

.. tab:: Arch Linux:

   .. CODE-BLOCK:: bash

       $ sudo pacman -S python-jsonschema

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install jsonschema

.. tab:: Debian/Ubuntu:

   .. CODE-BLOCK:: bash

       $ sudo apt-get install python3-jsonschema

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install python3-jsonschema

.. tab:: Gentoo Linux:

   .. CODE-BLOCK:: bash

       $ sudo emerge dev-python/jsonschema

.. tab:: MacPorts:

   .. CODE-BLOCK:: bash

       $ sudo port install py-jsonschema

.. tab:: openSUSE:

   .. CODE-BLOCK:: bash

       $ sudo zypper install python3\$\{PYTHON_MINOR\}-jsonschema

.. tab:: Void Linux:

   .. CODE-BLOCK:: bash

       $ sudo xbps-install python3-jsonschema

# See https://repology.org/project/python:jsonschema/versions

If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure`` will check if the system package can be used.
