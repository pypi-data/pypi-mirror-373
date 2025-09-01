# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from phenomxpy import __version__, __copyright__, __author__

project = "phenomxpy"
copyright = __copyright__
author = __author__
release = __version__

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.mathjax",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.viewcode",
    "sphinx.ext.doctest",
    "sphinx.ext.napoleon",
    "sphinxcontrib.bibtex",
    "myst_nb",
]

templates_path = ["_templates"]
exclude_patterns = []

mathjax3_config = {
    "loader": {"load": ["[tex]/physics"]},
    "tex": {
        "packages": {"[+]": ["physics"]},
        "macros": {},
    },
}


bibtex_bibfiles = ["bibliography.bib"]
bibtex_default_style = "unsrt"

nb_execution_mode = "off"

# Mock external modules
autodoc_mock_imports = [
    "bilby",
    "ldc",
    "scipy",
    "numba",
    "torch",
    "pytorch3d",
    "quaternion",
    "cupy",
    "numpy",
    "lalsimulation",
    "lalsimulation.gwsignal",
    "lalsimulation.gwsignal.core",
    "lalsimulation.gwsignal.core.waveform",
    "lal",
    "lalframe",
    "lalinference",
    "lalmetaio",
    "astropy",
    "gwpy",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

pygments_style = "sphinx"
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_logo = "_static/img/logo.svg"
html_favicon = "_static/img/favicon.ico"

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    "css/custom.css",
]


# -- Options for Latex output ------------------------------------------------

latex_elements = {
    "papersize": "a4paper",
    "figure_align": "htbp",
    "pointsize": "10pt",
    "preamble": r"""
        \usepackage{hyperref}
        \usepackage{graphicx}
        \usepackage{physics}
        \usepackage[print-unity-mantissa=false]{siunitx}
        """,
}
