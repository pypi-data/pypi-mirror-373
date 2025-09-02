Development
***********

.. _development:

Prerequisites
=============
Before you begin, ensure you have the following installed on your system:

- Python 3.10 or higher
- pip (Python package installer)

Installation
============

Creating a virtual environment
------------------------------
Creating a virtual environment is a best practice to isolate your project dependencies from the system-wide Python
installation:

#. Open a terminal or command prompt.
#. Navigate to the root directory of the project.
#. Run the following command to create a virtual environment:

   .. code-block:: bash

       python -m venv .venv

   This will create a virtual environment named ``.venv`` in your project directory.

#. Activate the virtual environment:

   - On Linux and macOS:

     .. code-block:: bash

         source .venv/bin/activate

   - On Windows:

     .. code-block:: powershell

         .venv\Scripts\activate


Installing the dependencies
---------------------------
With the virtual environment activated, you can now install the required dependencies.

Install the package in editable mode (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When installing this package in editable mode, the dependencies (listed in ``pyproject.toml``) will be automatically
installed. To install the package in editable mode run:

.. code-block:: bash

    pip install -e /path/to/project/root/

In case of problems when importing the library, you may need to use the compatibility mode:

.. code-block:: bash

    pip install -e /path/to/project/root/ --config-settings editable_mode=compat

Installing the package in editable mode will allow you to import it when the virtual environment in active, from any
path. This is especially useful when developing the package and building the documentation.

Install only the dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The package dependencies are listed in the ``requirements.txt`` file. Run the following command to install them:

.. code-block:: bash

    pip install -r requirements.txt

To develop ``dibisoreporting`` and ``dibisoplot`` in parallel, you may like to install ``dibisoplot`` in editable mode:

.. code-block:: bash

    pip install -e /path/to/dibisoplot/

In case of problems when importing ``dibisoplot``, you may need to use the compatibility mode:

.. code-block:: bash

    pip install -e /path/to/dibisoplot/ --config-settings editable_mode=compat

Building the documentation
==========================

The documentation is built with Sphinx.

To build it, you will need to install Sphinx with several other packages, and then build the documentation by calling
the makefile. During all those steps, you need to have the virtual environment activated.

You need to make sure that Make is installed on your computer (it usually is the case on Linux).

Install Sphinx dependencies
---------------------------

.. code-block:: bash

    pip install -r sphinx-doc/requirements.txt

Build
-----

Once everything is installed, go in the directory ``sphinx-doc`` and run the following command:

.. code-block:: bash

    make html

If needed, you can run ``make clean`` to rebuild from scratch the documentation.

Make a release
==============

1. Commit all changes to be included in the release
2. Update the version file ``dibisoreporting/_version.py`` with the new version identifier
3. Commit
4. Create a tag with Git: ``git tag -a vX.X.X -m "short description of changes"``
5. Push changes: ``git push`` then ``git push --tags``
6. On GitHub, go to the repository tags, and create a release from the new tag. You can put the same message as the one of the tag.
7. Check that the release is successfully published on GitHub and PyPI.
