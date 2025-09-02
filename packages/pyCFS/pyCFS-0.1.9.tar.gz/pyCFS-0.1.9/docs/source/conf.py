# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import pyCFS, sys

sys.path.append("../pyCFS")

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = pyCFS.__name__
copyright = "2024, Verein zur Förderung der Software openCFS"
author = " and ".join(pyCFS.__author__)
release = pyCFS.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "myst_parser",
    "sphinx.ext.autodoc",  # Parses (sub)modules
    "sphinx.ext.napoleon",  # Parses Numpy docstrings
    "sphinx.ext.mathjax",  # Print mathematical expressions
    "sphinx.ext.autosummary",  # Make module lists in table
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = []

myst_enable_extensions = ["colon_fence", "dollarmath", "amsmath"]
myst_heading_anchors = 3
myst_dmath_allow_labels = True
myst_dmath_double_inline = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_logo = "./_static/art/pyCFS_logo.svg"
html_favicon = "./_static/art/pyCFS_logo.svg"
html_title = "pyCFS Documentation"

html_theme_options = {
    "logo": {
        "text": f"pyCFS {release}",
        "image_light": html_logo,
        "image_dark": html_logo,
    },
    "icon_links": [
        {
            "name": "GitLab",
            "url": "https://gitlab.com/openCFS/pycfs",
            "icon": "fa-brands fa-square-gitlab",
            "type": "fontawesome",
        },
        {
            "name": "Home",
            "url": "https://opencfs.org/",
            "icon": "fa-solid fa-house",
            "type": "fontawesome",
        },
    ],
}

# suppress errors :
suppress_warnings = ["myst.header"]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = {"np": "numpy"}
napoleon_attr_annotations = True

# Autodoc settings
autoclass_content = "both"
autodoc_class_signature = "mixed"
autodoc_member_order = "groupwise"
autodoc_default_options = {
    "member-order": "groupwise",
    "special-members": "__init__",
    "undoc-members": True,
    "private-members": True,  # Add this to include private members
    # "exclude-members": "__weakref__",
}
autodoc_typehints = "description"
autodoc_typehints_format = "short"
