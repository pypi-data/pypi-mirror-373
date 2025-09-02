.. Copyright (C) 2025 @verzierf <francois.verzier@univ-grenoble-alpes.fr>

.. SPDX-License-Identifier: LGPL-3.0-or-later

.. _getting_started:

===============
Getting Started
===============

Here's a simple example to get you started with mater-data-providing:

This example shows how to:

1. Import the main functions
2. Create a basic dataset
3. Serialize it to JSON format
4. Save it locally

Project Structure
-----------------

First, create this project structure:

.. code-block:: text

   my-project/
   ├── main.py
   └── data/
       ├── variable_dimension/
       │   └── variable_dimension.json
       ├── dimension/
       │   └── dimension.json
       └── input_data/
           └── (output will be generated here)

Required Files
--------------

Create the following files in your project:

**Main Script**

.. literalinclude:: ../../../main.py
   :language: python
   :caption: main.py

**Dimension Configuration**

This file contains all the dimension elements (names: location, object and process) that can be used in input_data files.
The equivalence dictionary (optional) references all terms that are equivalent to the corresponding “value” key, so that it can be automatically replaced by the :func:`replace_equivalence <mater_data_providing.transformations.replace_equivalence>` function.
The `data-completion-tool <https://pypi.org/project/data-completion-tool/>`_ library used in the `mater <https://pypi.org/project/mater/>`_ framework works on the basis of parent-child inheritance.
Thus, the optional parents_values dictionary references the names of the parents of the corresponding “value” key.

Translated with DeepL.com (free version)

Here is a minimal example:

.. literalinclude:: ../../../data/dimension/dimension.json
   :language: json
   :caption: data/dimension/dimension.json

**Variable Dimension Configuration**

This file shows all aspects of each variable and specifies whether they are intensive or extensive. 
Intensive means that the parent's value is the average of the children's values and 
extensive means that the parent's value is the sum of the children's values.

The following example references all variables of the mater core framework:

.. literalinclude:: ../../../data/variable_dimension/variable_dimension.json
   :language: json
   :caption: data/variable_dimension/variable_dimension.json

Running the Example
-------------------

To create the JSON dataset, execute:

.. code-block:: bash

   python main.py

Expected Output
---------------

This will create the following file:

.. literalinclude:: ../../../data/input_data/main.json
   :language: json
   :caption: data/input_data/main.json