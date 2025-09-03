import os
import sys
import subprocess
import tomllib
from datetime import datetime
from pathlib import Path

# Add the project's src directory to sys.path
sys.path.insert(0, os.path.abspath("../../src"))

# -- Project information -----------------------------------------------------
pyproject_path = Path(__file__).parents[2] / "pyproject.toml"

with pyproject_path.open("rb") as f:
    pyproject_data = tomllib.load(f)

project = pyproject_data["project"]["name"]
# for static verioning
# release = pyproject_data["project"]["version"]

# for dynamic versioning
def get_version():
    try:
        result = subprocess.run(
            ["hatch", "version"],
            stdout=subprocess.PIPE,
            check=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Failed to get version from hatch: {e}")
        return "unknown"
release = get_version()

version = release

# Extract author names
authors = [author["name"] for author in pyproject_data["project"]["authors"]]

# Build copyright
year = datetime.now().year
authors_str = ", ".join(authors)
copyright = f"{year}, {authors_str}"
author = authors_str

# -- General configuration ---------------------------------------------------
extensions = [
    # 'sphinx.ext.autodoc',     # Include docstrings in the documentation
    "autoapi.extension",
    "sphinx.ext.napoleon",  # Support for Google and NumPy style docstrings
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.mathjax",  # Enable MathJax for LaTeX-style math
    "sphinx.ext.todo",  # Enable todo lists
    "sphinx_autodoc_typehints",  # Handle type hints in documentation
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# html_theme = 'sphinx_rtd_theme'
html_theme = "furo"
html_static_path = ["../_static"]
# Furo theme options
html_theme_options = {
    "light_logo": "heros_logo.svg",
    "dark_logo": "heros_logo.svg",
    "sidebar_hide_name": False,
}

# Autodoc settings
autoclass_content = "both"
# -- AutoAPI configuration ---------------------------------------------------
autoapi_type = "python"
autoapi_dirs = ["../../src"]  # Path to your source code
autoapi_add_toctree_entry = True  # Avoid duplicate toctree entries
autoapi_keep_files = False  # Keep intermediate reStructuredText files
# todo conf
todo_include_todos = True
