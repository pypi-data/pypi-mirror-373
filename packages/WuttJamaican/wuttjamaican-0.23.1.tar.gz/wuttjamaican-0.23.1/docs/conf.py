# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from importlib.metadata import version as get_version

project = "WuttJamaican"
copyright = "2023-2024, Lance Edgar"
author = "Lance Edgar"
release = get_version("WuttJamaican")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.programoutput",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "enum_tools.autoenum",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "alembic": ("https://alembic.sqlalchemy.org/en/latest/", None),
    "humanize": ("https://humanize.readthedocs.io/en/stable/", None),
    "mako": ("https://docs.makotemplates.org/en/latest/", None),
    "packaging": ("https://packaging.python.org/en/latest/", None),
    "python": ("https://docs.python.org/3/", None),
    "python-configuration": (
        "https://python-configuration.readthedocs.io/en/latest/",
        None,
    ),
    "rattail": ("https://docs.wuttaproject.org/rattail/", None),
    "rattail-manual": ("https://docs.wuttaproject.org/rattail-manual/", None),
    "rich": ("https://rich.readthedocs.io/en/latest/", None),
    "sqlalchemy": ("http://docs.sqlalchemy.org/en/latest/", None),
    "wutta-continuum": ("https://docs.wuttaproject.org/wutta-continuum/", None),
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
