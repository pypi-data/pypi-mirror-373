"""
Test query REST API reports.
"""

from test.test_app import TestApp

from test.utils import build_query_id

from ocqv.app import version


class TestAppQueryReport(TestApp):
    """
    Test case for the query REST API reports.
    """

    def test_report_valid(self):
        """
        Test whether a valid query parameter yields a "valid" verdict.
        """
        self.assertQueryReport(
            f"""
<?xml version="1.0" encoding="UTF-8"?>
<ocqv:QueryReport
    xmlns:ocqv="https://www.parcifal.dev/ns/oots-cs-query-validator/2025-08"
    version="{version()}"
    apiVersion="1.2.0"
    createdAt="NOT_TESTED">
    <ocqv:ParameterEvaluation
        name="queryId"
        value="{build_query_id("eb", "requirements-by-procedure-and-jurisdiction")}"
        verdict="valid" />
</ocqv:QueryReport>
            """,
            "/1.2.0/rest/search",
            build_query_id("eb", "requirements-by-procedure-and-jurisdiction"))

    def test_report_invalid(self):
        """
        Test whether an invalid query parameter yields an "invalid" verdict.
        """
        self.assertQueryReport(
            f"""
<?xml version="1.0" encoding="UTF-8"?>
<ocqv:QueryReport
    xmlns:ocqv="https://www.parcifal.dev/ns/oots-cs-query-validator/2025-08"
    version="{version()}"
    apiVersion="1.2.0"
    createdAt="NOT_TESTED">
    <ocqv:ParameterEvaluation
        name="queryId"
        value="{build_query_id("eb", "requirements-by-procedure-and-jurisdiction")}"
        verdict="valid" />
    <ocqv:ParameterEvaluation
        name="country-code"
        value="spam"
        verdict="invalid" />
</ocqv:QueryReport>
            """,
            "/1.2.0/rest/search",
            build_query_id("eb", "requirements-by-procedure-and-jurisdiction"),
            {"country-code": "spam"})

    def test_report_unknown(self):
        """
        Test whether a fake query parameter yields an "unknown" verdict.
        """
        self.assertQueryReport(
            f"""
<?xml version="1.0" encoding="utf-8"?>
<ocqv:QueryReport 
    xmlns:ocqv="https://www.parcifal.dev/ns/oots-cs-query-validator/2025-08" 
    version="{version()}"
    apiVersion="1.2.0"
    createdAt="NOT_TESTED">
    <ocqv:ParameterEvaluation 
        name="queryId"
        value="{build_query_id("eb", "requirements-by-procedure-and-jurisdiction")}"
        verdict="valid" />
    <ocqv:ParameterEvaluation
        name="spam"
        value="bacon"
        verdict="unknown" />
</ocqv:QueryReport>
            """,
            "/1.2.0/rest/search",
            build_query_id("eb", "requirements-by-procedure-and-jurisdiction"),
            {"spam": "bacon"})

    def test_report_missing(self):
        """
        Test whether a missing query parameter yields a "missing" verdict.
        """
        self.assertQueryReport(
            f"""
<?xml version="1.0" encoding="utf-8"?>
<ocqv:QueryReport 
    xmlns:ocqv="https://www.parcifal.dev/ns/oots-cs-query-validator/2025-08" 
    version="{version()}"
    apiVersion="1.2.0"
    createdAt="NOT_TESTED">
    <ocqv:ParameterEvaluation 
        name="queryId"
        value="{build_query_id("dsd", "dataservices-by-evidencetype-and-jurisdiction")}"
        verdict="valid" />
    <ocqv:ParameterEvaluation
        name="evidence-type-classification"
        verdict="missing" />
    <ocqv:ParameterEvaluation
        name="country-code"
        verdict="missing" />
</ocqv:QueryReport>
            """,
            "/1.2.0/rest/search",
            build_query_id("dsd",
                           "dataservices-by-evidencetype-and-jurisdiction"))
