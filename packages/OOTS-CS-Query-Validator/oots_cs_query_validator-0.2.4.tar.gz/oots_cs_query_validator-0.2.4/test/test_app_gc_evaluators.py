"""
Test the codelist-based evaluators.
"""

from unittest import TestCase

from ocqv.app import PROCEDURE_ID, COUNTRY_CODE, NUTS_CODE, LAU_CODE

class TestAppEvaluators(TestCase):
    """
    Test case for all codelist-based evaluators.
    """

    def test_procedure_id_valid(self):
        """
        Test for a valid procedure ID.
        """
        self.assertTrue(PROCEDURE_ID("R1"))

    def test_procedure_id_format_invalid(self):
        """
        Test for a procedure ID with an invalid format.
        """
        self.assertFalse(PROCEDURE_ID("spam"))

    def test_procedure_id_value_invalid(self):
        """
        Test for a procedure ID with an invalid value.
        """
        self.assertFalse(PROCEDURE_ID("ZZZZ9999"))

    def test_country_code_valid(self):
        """
        Test for a valid country code.
        """
        self.assertTrue(COUNTRY_CODE("NL"))

    def test_country_code_format_invalid(self):
        """
        Test for a country code with an invalid format.
        """
        self.assertFalse(COUNTRY_CODE("spam"))

    def test_country_code_value_invalid(self):
        """
        Test for a country code with an invalid value.
        """
        self.assertFalse(COUNTRY_CODE("FO"))

    def test_nuts_code_valid(self):
        """
        Test for a valid NUTS code.
        """
        self.assertTrue(NUTS_CODE("NL11"))

    def test_nuts_code_format_invalid(self):
        """
        Test for a NUTS code with an invalid format.
        """
        self.assertFalse(NUTS_CODE("spam"))

    def test_nuts_code_value_invalid(self):
        """
        Test for a NUTS code with an invalid value.
        """
        self.assertFalse(NUTS_CODE("ZZZZ9999"))

    def test_lau_code_valid(self):
        """
        Test for a valid LAU code.
        """
        self.assertTrue(LAU_CODE("GM0014"))

    def test_lau_code_format_invalid(self):
        """
        Test for a LAU code with an invalid format.
        """
        self.assertFalse(LAU_CODE("spam"))

    def test_lau_code_value_invalid(self):
        """
        Test for a LAU code with an invalid value.
        """
        self.assertFalse(LAU_CODE("FO1000"))
