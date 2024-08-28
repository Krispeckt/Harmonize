# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sphinx_book_theme

sys.path.insert(0, os.path.abspath('..'))

project = 'Harmonize'
copyright = '2024, Krista'
author = 'Krista'
release = '1.0.0'
master_doc = 'index'
projectlink = 'https://github.com/Krispeckt/Harmonize'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.
.. |maybecoro| replace:: This function *could be a* |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'enum_tools.autoenum',
    'sphinx_book_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

intersphinx_mapping = {
  'py': ('https://docs.python.org/3', None)
}

autodoc_member_order = 'bysource'
html_favicon = '_assets/icon.ico'

html_theme = 'sphinx_book_theme'
html_theme_path = [sphinx_book_theme.get_html_theme_path()]
html_logo = '_assets/icon.png'
html_title = "Made with 🧡"


html_theme_options = {
    "repository_url": 'https://github.com/Krispeckt/Harmonize',
    "use_repository_button": True
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_css_files = ['style.css']
html_show_sourcelink = False
