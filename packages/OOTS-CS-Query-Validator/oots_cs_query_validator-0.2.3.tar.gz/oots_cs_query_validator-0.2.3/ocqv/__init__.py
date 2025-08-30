"""
Some generic functions.
"""

import os

import tomli


def version():
    """
    Provide the current version of OCQV.

    :return: The current version of OCQV.
    """
    path = os.path.join(os.path.dirname(__file__), "../pyproject.toml")
    with open(path, "rb") as file:
        toml = tomli.load(file)
    assert ("project" in toml and "version" in toml["project"]), \
        "Missing version in pyproject.toml"
    return toml["project"]["version"]
