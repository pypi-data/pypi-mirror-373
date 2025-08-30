# Configuration file for the Sphinx documentation builder.
#
# To build .rst files for YMLEditor modules:
# Go to the projectroot folder (YMLEditor)
# sphinx-apidoc -o docs/source YMLEditor

import os
import sys

# Include the project root and module paths
sys.path.insert(0, os.path.abspath('../..'))

# Project Information
project = 'YMLEditor'

# Sphinx Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
autoclass_content = 'both'

# HTML Theme
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
