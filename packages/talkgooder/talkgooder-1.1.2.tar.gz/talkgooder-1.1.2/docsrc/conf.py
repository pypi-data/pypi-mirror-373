import os
import sys

sys.path.insert(0, os.path.abspath("../src/talkgooder"))
sys.path.insert(0, os.path.abspath(".."))

from _version import __version__ as version  # noqa E402 # type: ignore # won't exist until build

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
