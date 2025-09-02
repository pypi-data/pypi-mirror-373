.. Copyright (C) 2025 @verzierf <francois.verzier@univ-grenoble-alpes.fr>

.. SPDX-License-Identifier: LGPL-3.0-or-later

.. _installation:

============
Installation
============

Requirements
------------

mater-data-providing requires Python 3.12 or later.

We recommend using one virtual environment per Python project to manage dependencies and maintain isolation. 
You can use a package manager like `uv <https://docs.astral.sh/uv/>`_ to help you with library dependencies and virtual environments.

Install from PyPi
-----------------

.. tab-set::

    .. tab-item:: with uv (Recommended)
        :sync: uv

        Install the latest stable version from PyPI:

        .. code-block:: bash

           uv add mater-data-providing

    .. tab-item:: with pip
        :sync: pip

        Install the latest stable version from PyPI:

        .. code-block:: bash

           pip install mater-data-providing

Verify Installation
-------------------

Test your installation by running:

.. code-block:: python

   import mater_data_providing as mdp
   print(mdp.__version__)