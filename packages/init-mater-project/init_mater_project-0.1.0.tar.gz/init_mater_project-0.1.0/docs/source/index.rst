.. Copyright (C) 2025 @verzierf <francois.verzier@univ-grenoble-alpes.fr>

.. SPDX-License-Identifier: LGPL-3.0-or-later

.. mater-data-providing documentation master file, created by
   sphinx-quickstart on Fri May 30 15:35:22 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. To hide the the title header of a page, add to the top of the page:
.. :sd_hide_title: 

:html_theme.sidebar_secondary.remove: true

============================================
mater-data-providing |release| documentation
============================================

`mater-data-providing` is a library to help create and validate datasets for the **MATER** framework. 
Datasets are created as serialized json to be written locally or sent to the MATER database.

.. grid:: 1 2 3 3
    :gutter: 4
    :padding: 2 2 0 0
    :class-container: sd-text-center

    .. grid-item-card::  User Guide
        :shadow: md

        The *user guide* provides infromations on installing the library environment and creating your first dataset.

        +++

        .. button-ref:: user_guide
            :ref-type: ref
            :click-parent:
            :color: secondary
            :expand:

            To the user guide

    .. grid-item-card::  API Reference
        :shadow: md

        The reference guide contains a detailed description of public functions.

        +++

        .. button-ref:: api_reference
            :ref-type: ref
            :click-parent:
            :color: secondary
            :expand:

            To the reference guide

    .. grid-item-card::  Contributing
        :shadow: md

        Want to help us in our project ? See the contribution guidelines and welcome aboard !

        +++

        .. button-ref:: contributing
            :ref-type: ref
            :click-parent:
            :color: secondary
            :expand:

            To the contribution guide

.. toctree::
   :maxdepth: 4
   :hidden:

   user_guide/index
   api_reference
   contributing
