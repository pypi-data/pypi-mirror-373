# OOTS Common Services Query Validator

[![pipeline status](https://gitlab.com/parcifal/ocqv/badges/master/pipeline.svg)](https://gitlab.com/parcifal/ocqv/-/pipelines)
[![coverage report](https://gitlab.com/parcifal/ocqv/badges/master/coverage.svg)](https://gitlab.com/parcifal/ocqv/-/commits/master)
[![PyPI version](https://img.shields.io/pypi/v/oots-cs-query-validator)][pypi]
[![Docker version](https://img.shields.io/docker/v/pcfal/ocqv?label=docker)][docker]

The OCQV is a simple WSGI-based HTTP server that allows queries, meant for 
the Once-Only Technical System (OOTS) Common Services, to be validated. More 
specifically, this concerns queries to the Evidence Broker (EB) and the Data 
Services Directory. In this case, *validation* means that we check whether the 
query specifies all necessary parameters with the correct values so that the 
Common Services are able to provide a valid response.

[//]: # (A detailed description of the development of this tool can be found)
[//]: # ([here][memo].)

 > This software is published under the [AGPLv3.0 licence](LICENCE).

## Features

- Validates OOTS Common Services queries with XML-based reporting.
- Ensures all required parameters are present and correctly formatted.
- Runs as a standalone HTTP server or within a WSGI/Docker environment.
- Includes a lightweight development server for quick testing.

## Installation

Three methods of installation are available:

 1. **PyPI**<br>
    The validator is published on [PyPI][pypi] and can be installed with:
    ```bash
    pip install OOTS-CS-Query-Validator
    ```
 2. **Docker**<br>
    A prebuilt Docker image is available:
    [pcfal/ocqv][docker]<br>
    Example run:
    ```bash
    docker run -p 80:80 pcfal/ocqv:latest
    ```
 3. **From source**<br> 
    You can build the code yourself. Clone this repo, update the submodule, 
    and install with `pip`:
    ```bash
    git clone git@gitlab.com:parcifal/ocqv.git
    cd ocqv
    git submodule update --init --recursive
    pip install .
    ```

## Debugging

A very basic (and definitely not production-ready) web server is included
using `werkzeug`. This is ideal for development purposes. With OCQV 
installed from PyPI or directly from source (as described above), the server 
can be started using the `ocqv` command. Advanced users can also achieve 
this by running the `ocqv/app.py`-script directly. `ocqv` allows for some 
configuration through its arguments, all of which are shown with `ocqv --help`.

Example output:

```bash
usage: ocqv [-h] [-H HOST] [-p PORT] [-r] [-d] [-t]

Run the OOTS Common Services Query Validator development server.

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  hostname or IP address to bind to (default: localhost)
  -p PORT, --port PORT  port to listen on (default: 5000)
  -r, --no-reload       disable auto-reloader
  -d, --no-debug        disable interactive debugger
  -t, --threaded        enable multithreading
```

## Usage

For a more permanent setup, Docker is recommended.
Internally, the validator exposes:

 - HTTP socket at port 80
 - WSGI socket at port 5000

Example production-like run:

```bash
docker run -d --name ocqv -p localhost:80:80 pcfal/ocqv:latest
```

## API

The validator exposes an HTTP endpoint for validating queries. In debug-mode,
this defaults to http://localhost:5000/1.2.0/rest/search. Using `curl` or a
web browser, reports can be generated for queries. For example, consider the 
following (rather lengthy) URL.

```url
http://localhost:500/1.2.0/rest/search?queryId=urn:fdc:oots:dsd:ebxml-regrep:queries:dataservices-by-evidencetype-and-jurisdiction&evidence-type-classification=http://example.com&jurisdiction-admin-l2=spam&spam=bacon
```

The resulting report is as follows (notice that all possible variations of 
verdicts appear in the evaluation of the parameters):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ocqv:QueryReport xmlns:ocqv="https://www.parcifal.dev/ns/oots-cs-query-validator/2025-08"
                  version="0.1.0" 
                  apiVersion="1.2.0" 
                  createdAt="2025-08-12T20:47:00.581476+00:00">
    <ocqv:ParameterEvaluation name="queryId"
                              value="urn:fdc:oots:dsd:ebxml-regrep:queries:dataservices-by-evidencetype-and-jurisdiction"
                              verdict="valid"/>
    <ocqv:ParameterEvaluation name="evidence-type-classification"
                              value="http://example.com"
                              verdict="valid"/>
    <ocqv:ParameterEvaluation name="jurisdiction-admin-l2" 
                              value="spam" 
                              verdict="invalid"/>
    <ocqv:ParameterEvaluation name="spam" 
                              value="bacon" 
                              verdict="unknown"/>
    <ocqv:ParameterEvaluation name="country-code" 
                              verdict="missing"/>
</ocqv:QueryReport>
```

Queries for both the EB and the DSD are to be submitted to the same endpoint.
At this moment, only the 1.2.0-version of the query specification is 
available. A full overview of the available queries and parameters for both 
the [EB][eb] and the [DSD][dsd] are available on the [OOTS HUB][hub].

## Development

To work on the codebase locally, clone the repository and install the 
dependencies, including those needed for running the unit tests and the linter.

```bash
git clone git@gitlab.com:parcifal/ocqv.git
cd ocqv
git submodule --init --recursive
pip install .[dev]
```

To run the development server, run `python ocqv/app.py`.

Use the following command to run the unit tests.

```bash
python -m unittest discover -s test
```

Configuration for `pylint` is also supported, run it as follows.

```bash
pylint ocqv test
```

[memo]:   https://www.van-de-weerd.net/~michael/memo/ocqv.html
[pypi]:   https://pypi.org/project/OOTS-CS-Query-Validator/
[docker]: https://hub.docker.com/r/pcfal/ocqv

[eb]:  https://oots.pages.code.europa.eu/tdd/apidoc/evidence-broker
[dsd]: https://oots.pages.code.europa.eu/tdd/apidoc/data-services-directory
[hub]: https://ec.europa.eu/digital-building-blocks/sites/display/OOTS/OOTSHUB+Home
