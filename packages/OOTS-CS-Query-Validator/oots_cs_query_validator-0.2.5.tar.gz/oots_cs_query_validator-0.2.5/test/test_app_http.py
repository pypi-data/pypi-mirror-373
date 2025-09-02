"""
Test the basic HTTP behaviour.
"""

from test.test_app import TestApp


class TestAppHTTP(TestApp):
    """
    Testcase for all HTTP endpoints and methods.
    """

    def test_get_no_query_id_bad_request(self):
        """
        Test requests without a query ID.
        """
        self.assertStatusCode(400, "/1.2.0/rest/search")

    def test_post_method_not_allowed(self):
        """
        Test POST requests.
        """
        self.assertQueryStatusCode(
            405,
            "/1.2.0/rest/search",
            "urn:fdc:oots:eb:ebxml-regrep:queries:requirements-by-procedure-and-jurisdiction",
            method="post")

    def test_put_method_not_allowed(self):
        """
        Test PUT requests.
        """
        self.assertQueryStatusCode(
            405,
            "/1.2.0/rest/search",
            "urn:fdc:oots:eb:ebxml-regrep:queries:requirements-by-procedure-and-jurisdiction",
            method="put")

    def test_delete_method_not_allowed(self):
        """
        Test DELETE requests.
        """
        self.assertQueryStatusCode(
            405,
            "/1.2.0/rest/search",
            "urn:fdc:oots:eb:ebxml-regrep:queries:requirements-by-procedure-and-jurisdiction",
            method="delete")

    def test_patch_method_not_allowed(self):
        """
        Test PATCH requests.
        """
        self.assertQueryStatusCode(
            405,
            "/1.2.0/rest/search",
            "urn:fdc:oots:eb:ebxml-regrep:queries:requirements-by-procedure-and-jurisdiction",
            method="patch")
