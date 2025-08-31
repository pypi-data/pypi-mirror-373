import os
import sys

sys.path.insert(0, os.path.abspath("../src/talkgooder"))
sys.path.insert(0, os.path.abspath(".."))

# Try to get version from setuptools-scm generated file, fallback to dynamic import
try:
    from _version import __version__ as version  # noqa E402
except ImportError:
    # If _version.py doesn't exist (e.g., in CI), try to get version dynamically
    try:
        from setuptools_scm import get_version

        version = get_version(root="..")
    except ImportError:
        # Final fallback
        version = "unknown"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "myst_parser",
]

project = "talkGooder"
copyright = "2024, Brian Warner"
author = "Brian Warner"
release = version

html_theme = "sphinx_rtd_theme"
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_static_path = ["_static"]
