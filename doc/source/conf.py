# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("./../.."))


project = "TreeFiles"


extensions = ["sphinx.ext.autodoc", "sphinx_copybutton"]
autodoc_member_order = "bysource"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


html_theme = "sphinx_book_theme"

html_static_path = ["_static"]
html_theme_options = {
    "extra_navbar": None,
    "use_download_button": False,
    "use_fullscreen_button": False,
    "repository_url": "https://github.com/GaetanDesrues/TreeFiles",
}
html_show_copyright = False
html_show_sphinx = False
