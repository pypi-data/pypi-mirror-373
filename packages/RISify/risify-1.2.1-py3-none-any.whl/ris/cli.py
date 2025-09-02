#! /usr/bin/env python3

"""
Provide a CLI for generating RIS codes from the command-line.
"""
import logging
from argparse import ArgumentParser
from importlib import metadata
from pathlib import Path

import tomli

from .ris import _RISStr, _ENCODING_ASCII, _ENCODING_HTML, _ENCODING_UNICODE

LOGGING_LEVELS = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG
}


def _version() -> str:
    """
    Provide the current version of RISify.

    :return: The current version of RISify.
    """
    try:
        return metadata.version("RISify")
    except metadata.PackageNotFoundError:
        logging.debug("package not installed")

    path = Path(__file__).parent / ".." / "pyproject.toml"
    path = path.resolve()
    with open(path, "rb") as file:
        toml = tomli.load(file)
    if not ("project" in toml and "version" in toml["project"]):
        raise KeyError("missing version in pyproject.toml")
    return toml["project"]["version"]


def main():
    """
    Provide a CLI for converting strings to RIS codes.
    """

    parser = ArgumentParser(prog="ris",
                            description="Convert a country code to a RIS code.")

    encoding_group = parser.add_mutually_exclusive_group()
    encoding_group.add_argument("-a", "--ascii",
                                action="store_true",
                                help="output as a country code in "
                                     "lowercase ascii")
    encoding_group.add_argument("-A", "--ASCII",
                                action="store_true",
                                help="output as a country code in "
                                     "uppercase ascii")
    encoding_group.add_argument("-u", "--unicode",
                                action="store_true",
                                help="output as a ris code in unicode "
                                     "(default)")
    encoding_group.add_argument("-H", "--html",
                                action="store_true",
                                help="output as a ris code in html")

    parser.add_argument("-v", "--verbose",
                        action="count",
                        default=0,
                        help="increase verbosity")

    parser.add_argument("-l", "--output-log",
                        help="output log file (defaults to stdout)")

    parser.add_argument("-V", "--version",
                        action="version",
                        version=_version())

    parser.add_argument("value",
                        help="input text (ascii, ris or html) to convert")

    args = parser.parse_args()

    log_level = LOGGING_LEVELS.get(args.verbose, logging.DEBUG)

    logging.basicConfig(level=log_level, filename=args.output_log)
    logging.debug("verbosity level set to %d", args.verbose)

    uppercase = False

    if args.ascii:
        encoding = _ENCODING_ASCII
        logging.debug("lowercase ascii mode")
    elif args.ASCII:
        encoding = _ENCODING_ASCII
        uppercase = True
        logging.debug("uppercase ascii mode")
    elif args.html:
        encoding = _ENCODING_HTML
        logging.debug("html mode")
    else:
        encoding = _ENCODING_UNICODE
        logging.debug("unicode mode")

    try:
        result = _RISStr(args.value, encoding, uppercase)
    except ValueError as e:
        parser.error(str(e))

    print(result)


if __name__ == "__main__":
    main()
