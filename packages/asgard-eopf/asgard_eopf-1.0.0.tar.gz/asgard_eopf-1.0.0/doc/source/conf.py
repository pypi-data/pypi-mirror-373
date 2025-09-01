# pylint: skip-file
# flake8: noqa
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
# ~ import os
# ~ import sys

# ~ sys.path.insert(0, os.path.abspath("../.."))
# ~ sys.setrecursionlimit(1500)

# -- Project information -----------------------------------------------------

project = "asgard"
copyright = "2022-2023, CS GROUP"
author = "CS Group Team"

# The full version, including alpha/beta/rc tags
from importlib.metadata import distribution

try:
    version = distribution("asgard_eopf").version
    release = version
except Exception as error:
    print("WARNING: cannot find asgard version")
    version = "V0"
    release = version

# The master toctree document.
master_doc = "index"

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.ifconfig",  # add if config possibility in rst files
    "sphinx.ext.intersphinx",  # other projects automatic links to doc
    "sphinx.ext.mathjax",  # Add rst math capabilities with :math:
    "sphinx.ext.autodoc",  # apidoc automatic generation
    "sphinx.ext.viewcode",  # viewcode in automatic apidoc
    "myst_parser",
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


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "inverse_loc_problem.*"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

myst_heading_anchors = 3

# Enable MyST (Markdown to Rest) extensions
myst_enable_extensions = [
    # allow parsing $\LaTeX$ math
    "dollarmath",
    # enable tip and note generation
    "colon_fence",
]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Title
html_title = "asgard Documentation"
html_short_title = "asgard Documentation"

# Logo
# html_logo =

# Favicon
# html_favicon = "images/favicon_noname.ico"

# Theme options
html_theme_options = {
    "logo_only": True,
    "navigation_depth": 3,
}

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = ["custom.css"]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "asgardDoc"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    "papersize": "letterpaper",
    # The font size ('10pt', '11pt' or '12pt').
    "pointsize": "10pt",
    # Additional stuff for the LaTeX preamble.
    "preamble": "",
    # Latex figure (float) alignment
    "figure_align": "htbp",
}
numfig = True


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]

# api doc options
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Configuration for intersphinx
intersphinx_mapping = {
    "Python": ("https://docs.python.org/3/", None),
    "Distributed": ("https://distributed.dask.org/en/latest/", None),
    "Dask": ("https://docs.dask.org/en/latest/", None),
    "Gdal": ("https://gdal.org/", None),
    "jsonschema": ("https://python-jsonschema.readthedocs.io/en/latest/", None),
    "numpy": ("http://docs.scipy.org/doc/numpy", None),
}


def autodoc_process_docstring(app, what, name, obj, options, lines):
    """
    Used to fix docstrings on-the-fly when generatiing pages with sphinx
    See https://github.com/sphinx-doc/sphinx/issues/10151
    """
    for i in range(len(lines)):
        # Auto convert np.whatever into numpy.whatever in docstrings for sphinx
        lines[i] = lines[i].replace("np.", "numpy.")
        lines[i] = lines[i].replace("List[", "~typing.List[")
        lines[i] = lines[i].replace("Union[", "~typing.Union[")
        lines[i] = lines[i].replace("Set[", "~typing.Set[")
        lines[i] = lines[i].replace("Tuple[", "~typing.Tuple[")
        lines[i] = lines[i].replace("Generator[", "~typing.Generator[")


def setup(app):
    app.connect("autodoc-process-docstring", autodoc_process_docstring)
