"""
Tests for the test utils.
"""

from unittest import TestCase

from test.utils import build_query_id, build_query


class TestTestUtils(TestCase):
    """
    Test case for the test utils.
    """

    def test_build_query_id_eb(self):
        """
        Test building a query ID for the evidence broker.
        """
        self.assertEqual("urn:fdc:oots:eb:ebxml-regrep:queries:spam",
                         build_query_id("eb", "spam"))

    def test_build_query_id_dsd(self):
        """
        Test building a query ID for the data services directory.
        """
        self.assertEqual("urn:fdc:oots:dsd:ebxml-regrep:queries:spam",
                         build_query_id("dsd", "spam"))

    def test_build_query_id_fake_cs_assertion_error(self):
        """
        Test building a query ID for a fake common service.
        """
        with self.assertRaises(AssertionError):
            build_query_id("spam", "bacon")

    def test_build_query_empty_both(self):
        """
        Test building a query with an empty path and no parameters.
        """
        self.assertEqual("/", build_query("", {}))

    def test_build_query_path_empty_parameters(self):
        """
        Test building a query with a path and no parameters.
        """
        self.assertEqual("/spam", build_query("/spam", {}))

    def test_build_query_path_missing_leading_slash(self):
        """
        Test building a query with a path without a leading slash.
        """
        self.assertEqual("/spam", build_query("spam", {}))

    def test_build_query_path_single_parameter(self):
        """
        Test building a query with a path and a single parameter.
        """
        self.assertEqual("/spam?bacon=ham",
                         build_query("/spam", {"bacon": "ham"}))

    def test_build_query_path_multiple_parameters(self):
        """
        Test building a query with a path and multiple parameters.
        """
        self.assertEqual("/spam?bacon=ham&spam=eggs",
                         build_query("/spam", {
                             "bacon": "ham",
                             "spam": "eggs"
                         }))

    def test_build_query_path_repeating_parameters(self):
        """
        Test building a query with a parameter with multiple values.
        """
        self.assertEqual("/spam?bacon=ham&bacon=eggs",
                         build_query("/spam", {"bacon": ["ham", "eggs"]}))

    def test_build_query_path_preexisting_parameter(self):
        """
        Test building a query with a path that already has parameters.
        """
        self.assertEqual("/spam?bacon=ham&spam=eggs",
                         build_query("/spam?bacon=ham", {"spam": "eggs"}))

    def test_path_preexisting_repeating_parameter(self):
        """
        Test building a query with a path that already has a parameter with
        the same key as a new parameter.
        """
        self.assertEqual("/spam?bacon=ham&bacon=eggs",
                         build_query("/spam?bacon=ham", {"bacon": "eggs"}))
