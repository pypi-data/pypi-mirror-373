# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sys
import os

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "qolab"
copyright = "qolab developers"
author = "Eugeniy Mikhailov"
release = "0.33"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "autoapi.extension",
    "sphinx.ext.napoleon",
]
autoapi_dirs = ["../qolab"]
autoapi_keep_files = True

templates_path = ["_templates"]
exclude_patterns = []

sys.path.insert(0, os.path.abspath(".."))
autosummary_mock_imports = ["pandas", "universal_tsdb", "justpy", "ue9", "cachetools"]

napoleon_google_docstring = True
napoleon_numpy_docstring = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

smartquotes = False
# html_theme = 'alabaster'
# html_theme = 'sphinx_rtd_theme'
html_theme = "furo"
html_static_path = ["_static"]
