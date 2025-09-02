"""
Simple WSGI application for hosting the query evaluator. Will run an HTTP
server for development purposes if ran directly.
"""

import re
from pathlib import Path
from xml.etree.ElementTree import tostring

import tomli
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from werkzeug.wrappers import Request, Response

from .tools import QueryScheme, QueryReport
from .tools.parameter_evaluators import (defined, url, code_list,
                                         specification)

PATH_API_SEARCH = r"^/(\d+\.\d+\.\d+)/rest/search$"

PROCEDURE_ID = code_list("Procedures-CodeList.gc", r"^[A-Z]+[1-9][0-9]*$")
COUNTRY_CODE = code_list("EEA_Country-CodeList.gc", r"^[A-Z]{2}$")
NUTS_CODE = code_list("NUTS2024-CodeList.gc", r"^[A-Z][A-Z]+[0-9]+$")
LAU_CODE = code_list("LAU2022-CodeList.gc", r"^[A-Z]*[0-9]+$")

_QUERY_SCHEME_EB_REQUIREMENTS_1_0_0 = QueryScheme({
    "queryId": defined
}, {
    "procedure-id": PROCEDURE_ID,
    "country-code": COUNTRY_CODE,
    "jurisdiction-admin-l2": NUTS_CODE,
    "jurisdiction-admin-l3": LAU_CODE
})

_QUERY_SCHEME_EB_REQUIREMENTS_1_1_0 = _QUERY_SCHEME_EB_REQUIREMENTS_1_0_0
_QUERY_SCHEME_EB_REQUIREMENTS_1_2_0 = _QUERY_SCHEME_EB_REQUIREMENTS_1_1_0

_QUERY_SCHEME_EB_EVIDENCE_TYPES_1_0_0 = QueryScheme({
    "queryId": defined,
    "requirement-id": url
}, {
    "country-code": COUNTRY_CODE,
    "jurisdiction-admin-l2": NUTS_CODE,
    "jurisdiction-admin-l3": LAU_CODE
})

_QUERY_SCHEME_EB_EVIDENCE_TYPES_1_1_0 = _QUERY_SCHEME_EB_EVIDENCE_TYPES_1_0_0

_QUERY_SCHEME_EB_EVIDENCE_TYPES_1_2_0 = \
    _QUERY_SCHEME_EB_EVIDENCE_TYPES_1_1_0.extend({
        "requirement-id": None
    }, {
        "requirement-id": url,
        "jurisdiction-admin-l2": None,
        "jurisdiction-admin-l3": None
    })

_QUERY_SCHEME_DSD_DATASERVICES_1_0_0 = QueryScheme({
    "queryId": defined,
    "evidence-type-classification": url,
    "country-code": COUNTRY_CODE
}, {
    "jurisdiction-admin-l2": NUTS_CODE,
    "jurisdiction-admin-l3": LAU_CODE,
    "jurisdiction-context-id": defined,
    "evidence-type-id": defined,
    "EvidenceProviderClassification": defined
})

_QUERY_SCHEME_DSD_DATASERVICES_1_1_0 = \
    _QUERY_SCHEME_DSD_DATASERVICES_1_0_0.extend({}, {
        "specification": specification
    })

_QUERY_SCHEME_DSD_DATASERVICES_1_2_0 = \
    _QUERY_SCHEME_DSD_DATASERVICES_1_1_0.extend({}, {
        "evidence-type-id": None
    })

QUERY_SCHEMAS = {
    "urn:fdc:oots:eb:ebxml-regrep:queries:requirements-by-procedure-and-jurisdiction": {
        "1.2.0": _QUERY_SCHEME_EB_REQUIREMENTS_1_2_0,
        "1.1.0": _QUERY_SCHEME_EB_REQUIREMENTS_1_1_0,
        "1.0.0": _QUERY_SCHEME_EB_REQUIREMENTS_1_0_0
    },
    "urn:fdc:oots:eb:ebxml-regrep:queries:evidence-types-by-requirement-and-jurisdiction": {
        "1.2.0": _QUERY_SCHEME_EB_EVIDENCE_TYPES_1_2_0,
        "1.1.0": _QUERY_SCHEME_EB_EVIDENCE_TYPES_1_1_0,
        "1.0.0": _QUERY_SCHEME_EB_EVIDENCE_TYPES_1_0_0,
    },
    "urn:fdc:oots:dsd:ebxml-regrep:queries:dataservices-by-evidencetype-and-jurisdiction": {
        "1.2.0": _QUERY_SCHEME_DSD_DATASERVICES_1_2_0,
        "1.1.0": _QUERY_SCHEME_DSD_DATASERVICES_1_1_0,
        "1.0.0": _QUERY_SCHEME_DSD_DATASERVICES_1_0_0
    }
}


def version():
    """
    Provide the current version of OCQV.

    :return: The current version of OCQV.
    """
    path = Path(__file__).parent / ".." / "pyproject.toml"
    path = path.resolve()
    with open(path, "rb") as file:
        toml = tomli.load(file)
    if not ("project" in toml and "version" in toml["project"]):
        raise KeyError("missing version in pyproject.toml")
    return toml["project"]["version"]


@Request.application
def application(request: Request) -> Response:
    """
    Provides the WSGI application for the query evaluator.

    :param request: The request to handle.
    :return: An HTTP response.
    """
    match = re.fullmatch(PATH_API_SEARCH, request.path)

    if not match:
        raise NotFound("Path not found.")

    if "queryId" not in request.args:
        raise BadRequest("Query ID must be specified.")

    if any(len(request.args.getlist(k)) != 1 for k in request.args.keys()):
        raise BadRequest("Parameters can only be specified once.")

    query_id = str(request.args.get("queryId"))

    if query_id not in QUERY_SCHEMAS:
        raise NotFound("Query ID not found.")

    api_version = match.group(1)

    if api_version not in QUERY_SCHEMAS[query_id]:
        raise NotFound("API version not found.")

    if request.method not in ("GET", "HEAD"):
        raise MethodNotAllowed(valid_methods=("GET", "HEAD"))

    report = QueryReport({**request.args},
                         QUERY_SCHEMAS[query_id][api_version],
                         version(),
                         api_version).as_xml()

    return Response(tostring(report, encoding="utf-8", xml_declaration=True),
                    content_type="application/xml; charset=utf-8")
