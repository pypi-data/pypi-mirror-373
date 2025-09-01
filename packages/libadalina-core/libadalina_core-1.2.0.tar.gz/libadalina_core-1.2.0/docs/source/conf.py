# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import pathlib

sys.path.insert(0, os.path.abspath(pathlib.Path(__file__).parent.parent.parent))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'libadalina-core'
copyright = '2025, OptLab, University of Milan'
author = 'Marco Casazza, Alberto Ceselli, Marco Premoli'
release = '1.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    "sphinxcontrib.collections",
    'nbsphinx'
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Intersphinx settings
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable', None),
    'geopandas': ('https://geopandas.org/en/stable/', None),
    'pyspark': ('https://spark.apache.org/docs/latest/api/python/', None),
}

collections = {
    'notebooks': {
        'driver': 'copy_folder',
        'source': pathlib.Path(__file__).parent.parent.parent / 'examples',
        'target': 'notebooks',
        'ignore': ['*.py', '.sh'],
    }
}

templates_path = ['_templates']
exclude_patterns = ['_build', '**.ipynb_checkpoints']

nbsphinx_execute = 'never'  # Do not execute notebooks during build
highlight_language = 'python'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '10pt',
    'extraclassoptions': 'oneside',
    'fncychap': r'\usepackage[Bjornstrup]{fncychap}',
    'makeindex': r'\usepackage[columns=1]{idxlayout}\makeindex'
}