"""
Test query REST API statuses.
"""

from test.test_app import TestApp

from test.utils import build_query_id


class TestAppQuery(TestApp):
    """
    Test case for the query REST API statuses.
    """

    def test_fake_path_not_found(self):
        """
        Test whether a fake path is not found.
        """
        self.assertQueryStatusCode(
            404,
            "/1.0.2/spam/bacon",
            build_query_id("eb", "requirements-by-procedure-and-jurisdiction"))

    def test_fake_query_id_not_found(self):
        """
        Test whether a fake query ID results in a bad request.
        """
        self.assertQueryStatusCode(
            404,
            "/1.2.0/rest/search",
            build_query_id("eb", "eggs-bacon-and-ham"))

    def test_fake_version_not_found(self):
        """
        Test whether a fake version is not found.
        """
        self.assertQueryStatusCode(
            404,
            "/9.9.9/rest/search",
            build_query_id("eb", "requirements-by-procedure-and-jurisdiction"))

    def test_eb_requirements_ok(self):
        """
        Test whether a complete requirements query is OK.
        """
        self.assertQueryStatusCode(
            200,
            "/1.2.0/rest/search",
            build_query_id("eb", "requirements-by-procedure-and-jurisdiction"))

    def test_eb_evidence_types_ok(self):
        """
        Test whether a complete evidence types query is OK.
        """
        self.assertQueryStatusCode(
            200,
            "/1.2.0/rest/search",
            build_query_id("eb",
                           "evidence-types-by-requirement-and-jurisdiction"))

    def test_dsd_dataservices_ok(self):
        """
        Test whether a complete dataservices query is OK.
        """
        self.assertQueryStatusCode(
            200,
            "/1.2.0/rest/search",
            build_query_id("dsd",
                           "dataservices-by-evidencetype-and-jurisdiction"))
