# Configuration file for the Sphinx documentation builder.

# For the full list of built-in configuration values, see:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os, sys

# Add project root to path for sphinx autodoc
sys.path.insert(0, os.path.abspath('../'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'NB-QOL'
version = '0.1.0'
release = '0.1.0'
author = 'Colin Conwell'
copyright = '2025, Colin Conwell'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    'myst_parser',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

exclude_patterns = [
    'Thumbs.db',
    'build',  
    '.DS_Store'
]

templates_path = ['_templates']

# autodoc configuration
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
    'show-inheritance': True,
}

# autosummary configuration
autosummary_generate = True
autosummary_imported_members = True
autosummary_recursive = True
autosummary_output_dir = 'source/modules'
autosummary_generate_overwrite = True

# napoleon autodoc settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = "NB-QOL Documentation"
html_theme = 'sphinxawesome_theme'

html_permalinks_icon = '<span>#</span>'


html_static_path = ['_static']
html_js_files = ['custom.js']
html_css_files = ['styles/book.css']

# Theme-specific options
html_theme_options = {
    "main_nav_links": {
        "GitHub": "https://github.com/ColinConwell/NB-QOL",
    }
}

# -- Additional Formatting ----------------------------------------------------
add_module_names = False
python_use_unqualified_type_names = True

# Enable proper code highlighting
pygments_style = 'sphinx'
highlight_language = 'python3'

# Configure MyST parser
myst_enable_extensions = [
    "colon_fence",
    "dollarmath",
    "smartquotes",
]