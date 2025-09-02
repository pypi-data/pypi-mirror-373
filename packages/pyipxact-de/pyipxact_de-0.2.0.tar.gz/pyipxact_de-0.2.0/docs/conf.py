# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import json
import os
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

src = (Path(__file__).resolve().parents[1] / "src")
sys.path.insert(0, str(src))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Accellera IP-XACT DE (Design Environment)'
copyright = '©2025, Amal Khailtash'
author = 'Amal Khailtash'
# The full version, including alpha/beta/rc tags

def _read_pyproject_metadata(pyproject_path: Path) -> tuple[str, str]:
    """Read project name and version from a pyproject.toml file.

    Args:
        pyproject_path: Absolute path to the repository's pyproject.toml.

    Returns:
        A tuple of (package_name, version). Empty strings are returned if missing.
    """
    try:
        with pyproject_path.open("rb") as f:
            data: dict = tomllib.load(f)
    except Exception:
        return "", ""

    proj: dict | None = data.get("project") if isinstance(data, dict) else None
    if not isinstance(proj, dict):
        return "", ""
    name: str = str(proj.get("name") or "")
    ver: str = str(proj.get("version") or "")
    return name, ver


def _get_pypi_version(package_name: str, timeout: float = 2.5) -> str | None:
    """Return the latest published version for a package on PyPI.

    This uses PyPI's simple JSON API. Network errors or missing packages
    return None so doc builds remain resilient offline or before first release.

    Args:
        package_name: The PyPI package name to query.
        timeout: Timeout in seconds for the HTTP request.

    Returns:
        The version string if available, otherwise None.
    """
    if not package_name:
        return None
    url: str = f"https://pypi.org/pypi/{package_name}/json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            payload: dict = json.load(resp)
        info: dict | None = payload.get("info") if isinstance(payload, dict) else None
        ver: str | None = None
        if isinstance(info, dict):
            raw = info.get("version")
            if isinstance(raw, str) and raw.strip():
                ver = raw.strip()
        return ver
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return None
    except Exception:
        # Be conservative: never crash docs for unexpected issues
        return None


# Resolve versions: local (from pyproject) and latest published (from PyPI)
_repo_root: Path = Path(__file__).resolve().parents[1]
_pyproject_toml: Path = _repo_root / "pyproject.toml"
_pkg_name, _local_version = _read_pyproject_metadata(_pyproject_toml)

# Sphinx semantics: "version" is typically the project version, "release" is the full release string.
# We use the local version for "version" and the latest published PyPI version for "release" when available.
version = _local_version or "__version__"
release = _get_pypi_version(_pkg_name) or version


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.mathjax',
    'sphinx.ext.autodoc',
    'sphinx.ext.githubpages',
    # 'sphinx.ext.autosectionlabel',
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
html_css_files = [
    'css/custom.css',
]
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
# myst_enable_extensions: list[str] = [
#     "footnote",
#     # "colon_fence",
#     # "deflist",
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
