"""
This module defines the configuration of sphinx.

Copyright (C) 2025 @verzierf <francois.verzier@univ-grenoble-alpes.fr>

SPDX-License-Identifier: LGPL-3.0-or-later
"""

import os
import sys
from datetime import datetime

import mater_data_providing as mdp

sys.path.insert(0, os.path.abspath("../.."))

project = "mater-data-providing"
copyright = f"{datetime.now().year}, François Verzier"
author = "François Verzier"
release = str(mdp.__version__)

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",  # Handle Google/NumPy style docstrings
    # "sphinxcontrib.bibtex",
    "sphinx.ext.autosummary",
    "sphinx_copybutton",
    "sphinx_design",
    "myst_parser",
    "sphinx.ext.viewcode",
]

# # BibTeX configuration (common for both builders)
# bibtex_bibfiles = ["_static/biblio.bib"]
# bibtex_default_style = "plain"
# bibtex_reference_style = "author_year"

# MyST markdown extension
source_suffix = {
    ".rst": None,
    ".md": None,
}
myst_enable_extensions = ["colon_fence"]

# Generate autosummary pages
autosummary_generate = True

# # Add this to force generation of function pages
# autosummary_generate_overwrite = True

# Optional: configure autodoc to show more details
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# Autodoc settings (common for both builders)
autodoc_typehints = "description"
autodoc_class_signature = "separated"

# Common static path
html_static_path = ["_static"]

# -- HTML-specific configuration ---------------------------------------------
html_logo = "_static/MATER_logo.png"

html_theme_options = {
    "show_version_warning_banner": True,
    "navbar_align": "left",
    "show_prev_next": True,
    "secondary_sidebar_items": ["page-toc", "edit-this-page", "sourcelink"],
    "show_toc_level": 4,
    "icon_links": [
        {
            "name": "GitLab",
            "url": "https://gricad-gitlab.univ-grenoble-alpes.fr/isterre-dynamic-modeling/mater-project/data-providing",
            "icon": "fa-brands fa-gitlab",
            "type": "fontawesome",
        }
    ],
    "icon_links_label": "Quick Links",
}


# -- LaTeX-specific configuration --------------------------------------------
# latex_elements = {
#     "papersize": "a4paper",
#     "pointsize": "10pt",
#     "preamble": "",  # Clear any custom preamble
#     "maketitle": "",  # Exclude Sphinx title page
#     "tableofcontents": "",  # Exclude Sphinx-generated table of contents
# }
# sd_fontawesome_latex = True
toc_object_entries_show_parents = "hide"

napoleon_google_docstring = False
napoleon_numpy_docstring = True

# # This setting ensures the method name becomes a section
# autodoc_member_order = "bysource"

html_theme = "pydata_sphinx_theme"  # pydata_sphinx_theme alabaster
# master_doc = "technical_reference/model/index"  # uncomment to generate the documentation only for a subsection
