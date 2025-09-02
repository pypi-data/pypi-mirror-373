"""
OCQV init tests.
"""

import os
from unittest import TestCase

import tomli

from ocqv.app import version


class TestInit(TestCase):
    """
    Test helper functions in the OCQV init.
    """

    def test_version(self):
        """
        Test that the version is equal to the version in pyproject.toml.
        """
        path = os.path.join(os.path.dirname(__file__), "../pyproject.toml")
        with open(path, "rb") as file:
            toml = tomli.load(file)

        self.assertIn("project", toml,
                      "Project not in pyproject.toml")
        self.assertIn("version", toml["project"],
                      "Version not in pyproject.toml")
        self.assertEqual(toml["project"]["version"], version())
