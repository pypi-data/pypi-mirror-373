#!/usr/bin/python3
"""
Copyright (c) 2025 Penterep Security s.r.o.

ptresheaders - Response Header Parser

ptresheaders is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ptresheaders is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ptresheaders.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import os
import sys; sys.path.append(__file__.rsplit("/", 1)[0])
import re
import urllib
import inspect
import importlib

from typing import Literal

import requests
from bs4 import BeautifulSoup

from _version import __version__
from ptlibs import ptjsonlib, ptprinthelper, ptmisclib, ptnethelper

from ptlibs.ptprinthelper import ptprint, out_if

from modules.cors import CrossOriginResourceSharing
from modules.leaks import LeaksFinder

from ptcookiechecker.modules.cookie_tester import CookieTester

from collections import Counter

class PtResHeaders:
    """Script connects to target <url> and analyses response headers"""

    def __init__(self, args):
        self.ptjsonlib   = ptjsonlib.PtJsonLib()
        self.json        = args.json
        self.args        = args
        self.OBSERVED_HEADERS_MODULES, self.PREFIX_MAP = self.build_header_class_map(args.tests)
        self.DEPRECATED_HEADERS = ["X-Frame-Options", "X-XSS-Protection"]

    def run(self, args) -> None:
        """Main method"""

        response, dump = self.load_url(args)
        headers: dict = response.headers
        raw_headers: dict = response.raw.headers

        found_missing_headers: list = []
        found_deprecated_headers: set = set()
        found_duplicit_headers: list = []
        warnings: list = []


        # Print all response headers
        self.print_response_headers(raw_headers)
        self.print_meta_tags(response=response)

        # Print info leaking headers
        leaks_finder = LeaksFinder(args, self.ptjsonlib)
        leaks_finder.find_technology_headers(headers)
        leaks_finder.find_leaking_domains(headers)
        leaks_finder.find_ipv4(headers)

        # Test CORS
        CrossOriginResourceSharing().test(args=args, response_headers=headers)

        # Create a set to track processed headers (for duplicites)
        processed_headers = set()

        # Test observed headers for proper configuraton
        for observed_header, handler_function in self.OBSERVED_HEADERS_MODULES.items():
            #if handler_function == None: continue

            # Check if the header exists in the raw_headers dictionary (case-insensitive)
            if observed_header.lower() in (header.lower() for header in raw_headers.keys()):
                for header, header_values in raw_headers.items():
                    normalized_header = header.lower()
                    if normalized_header == observed_header.lower():
                        is_duplicate = normalized_header in processed_headers
                        handler_function(self.ptjsonlib, args, observed_header, header_values, response, is_duplicate).test_header(header_value=header_values)
                        processed_headers.add(normalized_header)
                if observed_header.lower() in [h.lower() for h in self.DEPRECATED_HEADERS]:
                    found_deprecated_headers.add(observed_header)

            # Observed header does not exists in response headers
            else:
                if observed_header == "X-DNS-Prefetch-Control":
                    continue
                if observed_header == "Content-Security-Policy-Report-Only":
                    continue

                # Special logic for Content-Security-Policy
                elif observed_header == "Content-Security-Policy":
                    # CSP and CSPRO not exists
                    if "Content-Security-Policy-Report-Only".lower() not in (header.lower() for header in raw_headers.keys()):
                        found_missing_headers.append(observed_header)
                        continue
                    # CSP not exists, CSPRO exists
                    if "Content-Security-Policy-Report-Only".lower() in (header.lower() for header in raw_headers.keys()):
                        warnings.append(f"'{observed_header}' header is missing, but 'Content-Security-Policy-Report-Only' is present.")
                        continue
                else:
                    found_missing_headers.append(observed_header)

        if "SC" in args.tests:
            ptprint(f"Set-Cookie:", "INFO", not self.args.json, colortext=True, newline_above=True)
            CookieTester().run(response, args, self.ptjsonlib)

        self.report_warnings(warnings, args)
        self.report_deprecated_headers(found_deprecated_headers, args)
        self.report_missing_headers(found_missing_headers, args)
        self.report_duplicate_headers(raw_headers, args)

        if not args.json and response.is_redirect:
            if self._yes_no_prompt("Returned response is an redirect, Scan again while following redirects? Y/n"):
                ptprint("\n\n\n", condition=not args.json, end="")
                args.redirects = True
                self.run(args)

        self.ptjsonlib.set_status("finished")
        ptprint(self.ptjsonlib.get_result_json(), "", self.json)

    def print_meta_tags(self, response):
        """Print all meta tags if text/html in content type"""
        content_type = next((value for key, value in response.headers.items() if key.lower() == "content-type"), "")
        if "text/html" not in content_type:
            return
        soup = BeautifulSoup(response.text, "lxml")
        meta_tags = soup.find_all("meta")
        if meta_tags:
            ptprint(f"Meta tags:", "TITLE", condition=not self.args.json, newline_above=True, indent=0, colortext=True)
            for meta in meta_tags:
                ptprint(meta, "ADDITIONS", condition=not self.args.json, colortext=True, indent=4)

    def load_url(self, args):
        try:
            response, dump = ptmisclib.load_url(args.url, args.method, data=args.data, headers=args.headers, cache=args.cache, redirects=args.redirects, proxies=args.proxy, timeout=args.timeout, dump_response=True)
            ptprint(f"Connecting to URL: {response.url}", "TITLE", not args.json, colortext=True, end=" ")
            ptprint(f"[{response.status_code}]", "TEXT", not args.json, end="\n")
            return (response, dump)
        except Exception as e:
            ptprint(f"Connecting to URL: {args.url}", "TITLE", not args.json, colortext=True, end=" ")
            ptprint(f"[err]", "TEXT", not args.json)
            self.ptjsonlib.end_error(f"Error retrieving response from server.", args.json)

    def report_warnings(self, warnings, args):
        ptprint(f"Warnings:", bullet_type="WARNING", condition=warnings and not args.json, newline_above=True)
        for warning_message in warnings:
            ptprint(warning_message, condition=not args.json, indent=8)
        ptprint(" ", condition=not args.json)

    def report_deprecated_headers(self, deprecated_headers, args):
        if deprecated_headers:
            ptprint(f"Deprecated security headers:", bullet_type="WARNING", condition=not args.json)
            for header in sorted(deprecated_headers):
                ptprint(f"{header}", bullet_type="TEXT", condition=not args.json, indent=8)
                #self.ptjsonlib.add_vulnerability(f"WARNIG-DEPRECATED-HEADER-{header}")
            ptprint(f" ", bullet_type="TEXT", condition=not args.json)

    def report_missing_headers(self, missing_headers, args):
        if missing_headers:
            ptprint(f"Missing security headers:", bullet_type="ERROR", condition=not args.json)
            for header in sorted(missing_headers):
                ptprint(f"{header}", bullet_type="TEXT", condition=not args.json, indent=8)
                #self.ptjsonlib.add_vulnerability(f"MISSING-HEADER-{header}")
                self.ptjsonlib.add_vulnerability(f"PTV-WEB-HTTP-{self.PREFIX_MAP[header]}MIS")

    def report_duplicate_headers(self, raw_headers, args):
        duplicit_headers: set = set()
        key_counts: dict = Counter(key for key, _ in raw_headers.items())
        for header_name, value in raw_headers.items():
            if key_counts.get(header_name, 0) > 1:
                if header_name.lower() == "set-cookie":
                    continue
                duplicit_headers.add(header_name)
        if duplicit_headers:
            ptprint(f"Duplicit headers:", "WARNING", not self.args.json, newline_above=True)
            for header_name in duplicit_headers:
                ptprint(header_name, "", not self.args.json, indent=8)

    def print_response_headers(self, headers: dict):
        """Print all response headers"""
        ptprint(f"Response Headers:", "INFO", not self.args.json, colortext=True)
        for header_name, header_value in headers.items():
            ptprint(f"{header_name}: {header_value}", "ADDITIONS", not self.args.json, colortext=True, indent=4)

    def _yes_no_prompt(self, message) -> bool:
        ptprint(message, "WARNING", not self.args.json, newline_above=True, end="")
        action = input(f': ').upper().strip()
        if action == "Y":
            return True
        elif action == "N":
            return False
        else:
            return True

    def _get_class_from_module(self, module) -> type:
        """
        Return the first class defined directly in the given module.
        Raises ValueError if no such class is found.
        """
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__:
                return obj
        raise ValueError(f"No class found in module {module.__name__}")

    def build_header_class_map(self, tests: list[str]) -> tuple[dict[str, type], dict[str, str]]:
        """
        Dynamically imports header modules whose prefixes match the given tests,
        and returns two dictionaries:
        - one mapping HTTP header names to their main classes
        - another mapping HTTP header names to their matching prefix (shortcut)

        Args:
            tests (list[str]): List of prefix strings to filter modules by (e.g., ['HSTS', 'CSP']).

        Returns:
            Tuple[dict[str, type], dict[str, str]]:
                - observed_headers:
                    Dictionary where keys are HTTP header names in Header-Case format 
                    (e.g., 'Strict-Transport-Security') and values are the corresponding 
                    main class objects from the modules.
                    Example:
                        {
                            'Strict-Transport-Security': <class StrictTransportSecurity>,
                            'Content-Security-Policy': <class ContentSecurityPolicy>
                        }

                - shortcuts:
                    Dictionary where keys are the same HTTP header names and values are
                    the matched prefix used to find the module (e.g., 'HSTS', 'CSP').
                    Example:
                        {
                            'Strict-Transport-Security': 'HSTS',
                            'Content-Security-Policy': 'CSP'
                        }
        """
        observed: dict[str, type] = {}
        shortcuts: dict[str, str] = {}

        full_modules = get_available_modules("full")  # e.g., 'HSTS_strict_transport_security'

        for full_name in full_modules:
            for prefix in tests:
                if full_name.startswith(prefix + "_"):
                    name = full_name.split("_", 1)[1]
                    header = "-".join(part.capitalize() for part in name.split("_"))

                    module_path = f"modules.headers.{full_name}"
                    module = importlib.import_module(module_path)

                    cls = self._get_class_from_module(module)
                    observed[header] = cls
                    shortcuts[header] = prefix
                    break  # no need to check further prefixes

        return observed, shortcuts

def get_help():
    """
    Generate structured help content for the CLI tool.

    This function dynamically builds a list of help sections including general
    description, usage, examples, and available options.

    Returns:
        list: A list of dictionaries, where each dictionary represents a section of help
              content (e.g., description, usage, options). The 'options' section includes
              available command-line flags and dynamically discovered test modules.
    """

    def _get_available_modules_help() -> list:
        """Return a list of rows describing available test modules.

        Each row has the structure: ["", "", test_code, label], where:
            - test_code is the uppercase prefix (e.g., " HSTS")
            - label is a human-readable test label (e.g., " Test Strict-Transport-Security")
        The list is sorted by test_code.
        """
        rows = []
        for module in get_available_modules("full"):
            if "_" in module and module.split("_", 1)[0].isupper():
                prefix, name = module.split("_", 1)
            else:
                prefix = ""
                name = module

            test_code = f" {prefix}" if prefix else ""
            label = f" {name.replace('_', '-').title()}"
            rows.append(["", "", test_code, label])

        # Hardcore set cookie test
        rows = sorted(rows, key=lambda x: x[2])
        rows.append(["", "", " SC", " Set-Cookie"])

        return rows

    return [
        {"description": ["Script connects to target <url> and analyses response headers"]},
        {"usage": ["ptresheaders <options>"]},
        {"usage_example": [
            "ptresheaders -u https://www.example.com",
            "ptresheaders -u https://www.example.com -p 127.0.0.1:8080",
        ]},
        {"options": [
            ["-u",  "--url",                    "<url>",            "Connect to URL"],
            ["-ts", "--test",                   "<test>",           "Specify headers to test (default all):"],
            *_get_available_modules_help(),
            ["",    "",                         "",                 ""],
            ["-p",  "--proxy",                  "<proxy>",          "Set proxy"],
            ["-c",  "--cookie",                 "<cookie>",         "Set cookie"],
            ["-H",  "--headers",                "<header:value>",   "Set headers"],
            ["-d",  "--data",                   "<data>",           "Send request data"],
            ["-T",  "--timeout",                "",                 "Set timeout"],
            ["-m",  "--method",                 "",                 "Set method (default GET)"],
            ["-a",  "--user-agent",             "<agent>",          "Set User-Agent"],
            ["-r",  "--redirects",              "",                 "Follow redirects"],
            ["-C",  "--cache",                  "",                 "Enable HTTP cache"],
            ["-j",  "--json",                   "",                 "Enable JSON output"],
            ["-v",  "--version",                "",                 "Show script version and exit"],
            ["-h",  "--help",                   "",                 "Show this help message and exit"],
        ]
        }]


def get_available_modules(mode: Literal["full", "prefix", "name", "header"] = "full") -> list[str]:
    """Return a list of available module names based on the selected mode.

    mode:
        - "full":   full module names without .py (e.g., HSTS_strict_transport_security)
        - "prefix": only prefixes (e.g., HSTS)
        - "name":   only names without prefixes (e.g., strict_transport_security)
        - "header": names formatted as HTTP headers (e.g., Strict-Transport-Security)
    """
    modules_folder = os.path.join(os.path.dirname(__file__), "modules", "headers")
    module_names = [
        f.rsplit(".py", 1)[0]
        for f in sorted(os.listdir(modules_folder))
        if f.endswith(".py") and not f.startswith("_")
    ]
    #module_names.append("SC")


    match mode:
        case "prefix":
            return [name.split("_", 1)[0] for name in module_names]
        case "name":
            return [name.split("_", 1)[1] for name in module_names if "_" in name]
        case "header":
            return [
                "-".join(part.capitalize() for part in name.split("_", 1)[1].split("_"))
                for name in module_names if "_" in name
            ]
        case _:
            return module_names


def parse_args():
    _header_choices = list(dict.fromkeys(get_available_modules("prefix"))) + ["SC"]
    parser = argparse.ArgumentParser(add_help="False", description=f"{SCRIPTNAME} <options>")
    exclusive = parser.add_mutually_exclusive_group(required=True)
    exclusive.add_argument("-u",  "--url",         type=str)
    parser.add_argument("-ts",  "--tests",         type=str, nargs="+", default=_header_choices, choices=_header_choices, metavar="")
    parser.add_argument("-m",  "--method",         type=str.upper, default="GET")
    parser.add_argument("-p",  "--proxy",          type=str)
    parser.add_argument("-d",  "--data",           type=str)
    parser.add_argument("-T",  "--timeout",        type=int, default=10)
    parser.add_argument("-a",  "--user-agent",     type=str, default="Penterep Tools")
    parser.add_argument("-c",  "--cookie",         type=str)
    parser.add_argument("-H",  "--headers",        type=ptmisclib.pairs, nargs="+")
    parser.add_argument("-r",  "--redirects",      action="store_true")
    parser.add_argument("-C",  "--cache",          action="store_true")
    parser.add_argument("-j",  "--json",           action="store_true")
    parser.add_argument("-v",  "--version",        action='version', version=f'{SCRIPTNAME} {__version__}')

    parser.add_argument("--socket-address",        type=str, default=None)
    parser.add_argument("--socket-port",           type=str, default=None)
    parser.add_argument("--process-ident",         type=str, default=None)


    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        ptprinthelper.help_print(get_help(), SCRIPTNAME, __version__)
        sys.exit(0)

    args = parser.parse_args()
    args.headers = ptnethelper.get_request_headers(args)
    args.headers.update({"Referer": "https://www.example.com/", "Origin": "https://www.example.com/"})
    args.timeout = args.timeout if not args.proxy else None
    args.proxy = {"http": args.proxy, "https": args.proxy}

    ptprinthelper.print_banner(SCRIPTNAME, __version__, args.json)
    return args

def main():
    global SCRIPTNAME
    SCRIPTNAME = "ptresheaders"
    requests.packages.urllib3.disable_warnings()
    args = parse_args()
    script = PtResHeaders(args)
    script.run(args)


if __name__ == "__main__":
    main()
