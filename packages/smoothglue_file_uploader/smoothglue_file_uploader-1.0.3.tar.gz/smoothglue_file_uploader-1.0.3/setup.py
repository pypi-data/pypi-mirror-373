"""Setup file to satisfy build requirements"""

import tomli
from setuptools import setup

with open("pyproject.toml", "r", encoding="utf-8") as f:
    pyproject = tomli.loads(f.read())

with open("README.md", "r", encoding="utf-8") as f:
    description = f.read()

setup_kwargs = {
    "name": pyproject["project"]["name"],
    "version": pyproject["project"]["version"],
    "description": pyproject["project"]["description"],
    "author": pyproject["project"]["authors"][0]["name"],
    "packages": pyproject["tool"]["setuptools"]["packages"],
    "install_requires": pyproject["project"]["dependencies"],
    "python_requires": pyproject["project"]["requires-python"],
    "long_description": description,
    "long_description_content_type": "text/markdown",
}
setup(**setup_kwargs)
