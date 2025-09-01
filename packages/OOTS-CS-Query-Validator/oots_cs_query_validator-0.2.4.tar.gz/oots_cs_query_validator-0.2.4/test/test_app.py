"""
Provide a base for testing the query evaluator through HTTP.
"""

from abc import ABC
from unittest import TestCase
from xml.etree import ElementTree

from test.utils import build_query

from werkzeug.test import Client
from werkzeug.wrappers import Response

from ocqv.app import application

_XMLNS = "https://www.parcifal.dev/ns/oots/cs/query-validator/2025-08"

class TestApp(ABC, TestCase):
    """
    Base class for testing the query evaluator through HTTP. Provides
    functions to assert HTTP status codes and query responses.
    """

    def setUp(self):
        self.app = Client(application, Response)  # type: ignore[arg-type]

    # pylint: disable=invalid-name
    def assertStatusCode(self,
                         status_code: int,
                         path: str,
                         params: dict=None,
                         method: str = "get") -> None:
        """
        Assert that requesting the application at the specified path with the
        specified parameters will yield the specified HTTP status code.

        :param status_code: The expected HTTP status code.
        :param path: The path to the validator.
        :param params: The query parameters.
        :param method: The HTTP method to use.
        """
        path = build_query(path, params)

        assert hasattr(self.app, method)
        request = getattr(self.app, method)

        assert callable(request)
        response = request(path)

        assert hasattr(response, "status_code")
        self.assertEqual(status_code, response.status_code)

    # pylint: disable=invalid-name
    def assertQueryStatusCode(self,
                              status_code: int,
                              path: str,
                              query_id: str,
                              params: dict = None,
                              **kwargs) -> None:
        """
        Assert that querying the validator at the specified path with the
        specified query ID and parameters will yield the specified HTTP status
        code.

        :param status_code: The expected HTTP status code.
        :param path: The path to the validator.
        :param query_id: The query ID.
        :param params: The query parameters.
        :param kwargs: Named arguments to be passed to assertStatusCode.
        """
        if params is None:
            params = {}

        params.update({
            "queryId": query_id
        })

        self.assertStatusCode(status_code, path, params, **kwargs)

    # pylint: disable=invalid-name
    def assertQueryReport(self,
                          expected: str,
                          path: str,
                          query_id: str,
                          params: dict = None) -> None:
        """
        Assert that the specified report is equal to the report requested from
        the query validator at the specified path, with the specified query ID
        and parameters. Note that equal formatting or ordering of elements or
        attributes is not required, each will be compared individually, however
        each attribute and element MUST appear in both reports. One exception
        is the `createdAt` attribute of the QueryReport element: it must
        appear but its value is not validated. This is due to the precision
        of this attribute's value, which therefor cannot be specified
        beforehand.

        :param expected: The expected report in XML format.
        :param path: The path to the query validator.
        :param query_id: The ID of the query to validate.
        :param params: The parameters for the query to validate.
        """
        if params is None:
            params = {}

        params.update({
            "queryId": query_id
        })

        response = self.app.get(build_query(path, params))

        assert response.status_code == 200, "HTTP status is invalid"

        expected_report = ElementTree.fromstring(expected.strip())
        response_report = ElementTree.fromstring(response.text.strip())

        self.assertEqual(expected_report.tag, response_report.tag,
                         "Incorrect XML tag or namespace")

        expected_attr = expected_report.attrib.copy()
        response_attr = response_report.attrib.copy()

        self.assertIn("createdAt", response_attr,
                      "Missing `createdAt` attribute")

        del expected_attr["createdAt"]
        del response_attr["createdAt"]

        self.assertEqual(expected_attr, response_attr,
                         "Inequal report attributes")

        for response_evaluation in response_report:
            self.assertIn("name", response_evaluation.attrib,
                          "Missing name for evaluation")

            name = response_evaluation.attrib["name"]
            asserted = False

            for expected_evaluation in expected_report:
                if name != expected_evaluation.attrib["name"]:
                    continue

                self.assertEqual(expected_evaluation.tag,
                                 response_evaluation.tag,
                                 "Incorrect XML tag or namespace")
                self.assertEqual(expected_evaluation.attrib,
                                 response_evaluation.attrib,
                                 "Inequal evaluation attributes")

                asserted = True
                break

            if not asserted:
                self.fail(f"Unknown evaluation `{name}`")
