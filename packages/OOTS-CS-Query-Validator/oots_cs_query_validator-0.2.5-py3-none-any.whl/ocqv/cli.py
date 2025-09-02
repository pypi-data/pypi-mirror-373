"""
Wraps the werkzeug application in a simple CLI for debugging purposes.
"""

from argparse import ArgumentParser

from werkzeug.serving import run_simple

from .app import version, application


def main():
    """
    Run the validator in a simple HTTP server, for debugging and development
    purposes.
    """
    parser = ArgumentParser(prog="ocqv",
                            description="Run the OOTS Common Services Query "
                                        "Validator development server.")

    parser.add_argument("-H", "--host", default="localhost",
                        help="hostname or IP address to bind to (default: "
                             "%(default)s)")
    parser.add_argument("-p", "--port", type=int, default=5000,
                        help="port to listen on (default: %(default)s)")
    parser.add_argument("-r", "--no-reload", action="store_true",
                        help="disable auto-reloader")
    parser.add_argument("-d", "--no-debug", action="store_true",
                        help="disable interactive debugger")
    parser.add_argument("-t", "--threaded", action="store_true",
                        help="enable multithreading")
    parser.add_argument("-v", "--version", action="version",
                        version=version())

    args = parser.parse_args()

    run_simple(args.host,
               args.port,
               application,
               use_reloader=not args.no_reload,
               use_debugger=not args.no_debug,
               threaded=args.threaded)


if __name__ == "__main__":
    main()
