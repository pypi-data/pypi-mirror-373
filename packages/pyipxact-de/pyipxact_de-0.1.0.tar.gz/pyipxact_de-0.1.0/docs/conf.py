# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

src = (Path(__file__).resolve().parents[1] / "src")
sys.path.insert(0, str(src))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Accellera IP-XACT DE (Design Environment)'
copyright = '©2025, Amal Khailtash'
author = 'Amal Khailtash'
# The full version, including alpha/beta/rc tags
version = "__version__"
release = "get_pypi_version(project)"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.mathjax',
    'sphinx.ext.autodoc',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosectionlabel',
    'sphinx_rtd_theme',
    'sphinx.ext.napoleon',
    'sphinx_contributors',
    'sphinx_github_changelog',
    # Enable Markdown (MyST) support so we can include README.md
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Treat broken references strictly to keep docs healthy, but suppress known noisy duplicates
nitpicky = False  # set True later once docs are clean
suppress_warnings = [
    # Autodoc can emit duplicate object descriptions for attributes when both class and members are documented
    'autodoc.object',
]

# Avoid duplicate section labels like "Subpackages" across different documents
# by prefixing labels with the document path (e.g., api/amal.eda:Subpackages).
# This resolves warnings such as:
#   WARNING: duplicate label subpackages, other instance in docs/api/amal.rst
autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 2


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']
# html_css_files = [
#     'css/custom.css',
# ]
# html_js_files = [
#     'js/sidebar-resize.js',
#     'js/theme-toggle.js',
# ]


# -- Extension configuration -------------------------------------------------
html_show_sourcelink = False
html_logo = "_static/logo-navbar.png"

html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',  #  Provided by Google in your dashboard
    'logo_only': True,
    # 'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'style_nav_header_background': '#2980B9',
    # Toc options
    # Keep navigation expanded so deep API pages don't cause the sidebar to disappear
    'collapse_navigation': False,
    'sticky_navigation': True,
    # Show deeper levels so package -> module -> class hierarchies remain in the sidebar
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
}

# Always render a global ToC in the left sidebar so navigation doesn't disappear
html_sidebars = {
    "**": [
        "globaltoc.html",
        "relations.html",
        "searchbox.html",
    ]
}

html_context = {
    'display_github': True,           # Integrate GitHub
    'github_user': 'amal-khailtash',  # Username
    'github_repo': "pyipxact-de",     # Repo name
    'github_version': 'main',         # Version
    'conf_py_path': '/docs/',         # Path in the checkout to the docs root
}
html_favicon = '_static/logo.svg'


# -- autodoc configuration -------------------------------------------------

# Make autodoc more helpful and resilient.
# Note: values can be bool or str (e.g., for 'member-order' or 'exclude-members'),
# so keep the type broad enough.
autodoc_default_options: dict[str, object] = {
    "members": True,
    "undoc-members": True,
    "inherited-members": True,
    "show-inheritance": True,
    # Exclude auto-generated inner classes that frequently collide across modules
    # and produce duplicate object description warnings. This keeps the index clean
    # while preserving primary classes and functions.
    "exclude-members": (
        "Meta, Value, Group, TransportMethods, TransportMethod, "
        "ApiType, AccessType, SubsetOnly, AccessHandles, Bank, BankDefinitionRef, LgiAccessType"
    ),
}
autodoc_typehints: str = "description"  # keep signatures clean
napoleon_google_docstring: bool = True
napoleon_numpy_docstring: bool = False
napoleon_use_ivar: bool = True
napoleon_use_admonition_for_examples: bool = True
napoleon_custom_sections: list[tuple[str, str]] = [
    ("Attributes", "other"),  # render Attributes as plain section to avoid duplicate attribute targets
]

# -- sphinx-github-changelog configuration ---------------------------------
# Pick up the GitHub token from environment so the changelog can be built
# both locally and in CI without hardcoding secrets.
# See: https://pypi.org/project/sphinx-github-changelog/
sphinx_github_changelog_token: str | None = os.getenv("SPHINX_GITHUB_CHANGELOG_TOKEN")

# -- MyST (Markdown) configuration -----------------------------------------
# Keep configuration minimal; we only need mdinclude to pull in README.md
# You can enable more extensions later if needed.
# Example (commented):
# myst_enable_extensions = [
#     "colon_fence",
#     "deflist",
# ]

# Mock optional/heavy imports that may not be present at doc build time.
def _compute_autodoc_mock_imports(modules: list[str]) -> list[str]:
    """Return the subset of modules that are not importable and should be mocked."""
    missing: list[str] = []
    for mod in modules:
        try:
            __import__(mod)
        except Exception:
            missing.append(mod)
    return missing

# Extend this list as needed if autodoc import warnings appear.
_optional_modules: list[str] = [
    "anyio",
    "fastapi",
    "lxml",  # if not installed locally
    "orjson",
    "pydantic",
    "PyQt5",
    "qtawesome",
    "qtpy",
    "sniffio",
    "starlette",
    "ujson",
    "uvicorn",
]
autodoc_mock_imports: list[str] = _compute_autodoc_mock_imports(_optional_modules)
