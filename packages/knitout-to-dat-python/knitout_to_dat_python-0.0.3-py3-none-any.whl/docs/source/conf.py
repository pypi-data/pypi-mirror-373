import os
import sys
from importlib.metadata import PackageNotFoundError, version

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('.'))

project = 'Knitout-to-DAT'
copyright = '2025, Megan Hofmann'
author = 'Megan Hofmann'

try:
    # Get version from installed package metadata
    # This reads from pyproject.toml when the package is installed
    version = version("knitout-to-dat-python")
except PackageNotFoundError:
    # Package is not installed (e.g., during development)
    # This happens when running from source without installation
    version = "0.0.0+dev"

release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # Core autodoc functionality
    'sphinx.ext.autosummary',  # Generate summary tables
    'sphinx.ext.viewcode',  # Add source code links
    'sphinx.ext.napoleon',  # Support for Google and NumPy style docstrings
    'sphinx.ext.intersphinx',  # Link to other projects' documentation
    'sphinx.ext.githubpages',  # Publish to GitHub pages
    'sphinx.ext.todo',  # Support for TODO items
    'sphinx.ext.coverage',  # Check documentation coverage
    'sphinx.ext.doctest',  # Test code snippets in documentation
    'sphinx_autodoc_typehints',  # Better type hint support
    'myst_parser',  # Support for Markdown files
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix(es) of source filenames
source_suffix = {
    '.rst': None,
    '.md': 'myst_parser',
}

# The master toctree document
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'  # ReadTheDocs theme
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 6,
    'includehidden': True,
    'titles_only': False
}

# -- Extension configuration -------------------------------------------------

# -- Options for autodoc ----------------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
    'inherited-members': False,  # Changed to False to reduce clutter
    'ignore-module-all': False,
}

# Don't show class signature with the class' name.
autodoc_class_signature = "mixed"

# Control the order of content in module documentation
autodoc_member_order = 'bysource'

# FIXED: Add proper type hint handling
autodoc_typehints = 'description'  # Show type hints in parameter descriptions
autodoc_typehints_description_target = 'documented'
autodoc_preserve_defaults = True

# -- Options for autosummary ------------------------------------------------
autosummary_generate = True
autosummary_imported_members = True

# Template for autosummary to control ordering
autosummary_context = {
    'content_first': True  # Custom context variable for templates
}

# -- Options for napoleon (Google/NumPy style docstrings) -------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False  # Focus on Google style only
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True  # Better formatting for examples
napoleon_use_admonition_for_notes = True     # Better formatting for notes
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True  # FIXED: Changed to True for better type processing
napoleon_type_aliases = None
napoleon_attr_annotations = True
napoleon_custom_sections = None

# -- Options for intersphinx extension ---------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'typing': ('https://typing.readthedocs.io/en/latest/', None),
}

# -- Options for todo extension ----------------------------------------------
todo_include_todos = True

# -- Options for typehints ---------------------------------------------------
typehints_fully_qualified = False
always_document_param_types = True
typehints_document_rtype = True
typehints_use_rtype = True
# ADDED: Additional typehint settings for better rendering
typehints_defaults = 'comma'
typehints_use_signature = True
typehints_use_signature_return = True

# -- Options for coverage extension ------------------------------------------
coverage_ignore_modules = []
coverage_ignore_functions = []
coverage_ignore_classes = []

# -- Custom configuration ----------------------------------------------------

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = ['knitout_to_dat_python.']  # FIXED: Updated to match your package name


# Custom autodoc processing to reorder content
def autodoc_skip_member(app, what, name, obj, skip, options):
    """Custom function to control member inclusion and ordering."""
    return skip


def setup(app):
    """Custom Sphinx setup function."""
    # Connect autodoc skip member function
    app.connect('autodoc-skip-member', autodoc_skip_member)
