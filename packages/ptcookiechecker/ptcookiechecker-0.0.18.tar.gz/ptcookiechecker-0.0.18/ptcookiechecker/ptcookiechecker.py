#!/usr/bin/python3
"""
    Copyright (c) 2024 Penterep Security s.r.o.

    ptcookiechecker - Cookie security testing tool

    ptcookiechecker is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ptcookiechecker is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ptcookiechecker.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import re
import sys; sys.path.append(__file__.rsplit("/", 1)[0])

import urllib

import requests

from _version import __version__
from ptlibs import ptjsonlib, ptprinthelper, ptmisclib, ptnethelper
from ptlibs.http.http_client import HttpClient

from modules.cookie_tester import CookieTester


class PtCookieChecker:
    def __init__(self, args):
        self.ptjsonlib   = ptjsonlib.PtJsonLib()
        self.use_json    = args.json
        self.timeout     = args.timeout
        self.cache       = args.cache
        self.args        = args

    def run(self, args) -> None:
        response, dump = self.send_request(args.url)
        self.cookie_tester = CookieTester()
        self.cookie_tester.run(response, args, self.ptjsonlib, test_cookie_issues=not args.list_cookies_only, filter_cookie=args.cookie_name)

        self.ptjsonlib.set_status("finished")
        ptprinthelper.ptprint(self.ptjsonlib.get_result_json(), "", self.use_json)

    def send_request(self, url: str) -> requests.models.Response:
        ptprinthelper.ptprint(f"Testing cookies for URL: {url}", bullet_type="TITLE", condition=not self.use_json, flush=True, colortext=True, end=" ")
        try:
            response, response_dump = ptmisclib.load_url_from_web_or_temp(url, method="GET", headers=self.args.headers, proxies=self.args.proxy, timeout=self.timeout, redirects=True, verify=False, cache=self.cache, dump_response=True)
            ptprinthelper.ptprint(f"[{response.status_code}]", condition=not self.use_json, colortext=False)
            return response, response_dump
        except requests.RequestException:
            ptprinthelper.ptprint(f"[error]", condition=not self.use_json, colortext=False)
            self.ptjsonlib.end_error(f"Cannot connect to server", self.use_json)

def get_help():
    return [
        {"description": ["Cookie security testing tool"]},
        {"usage": ["ptcookiechecker <options>"]},
        {"usage_example": [
            "ptcookiechecker -u https://www.example.com/",
            "ptcookiechecker -u https://www.example.com/ -c PHPSESSID -l",
        ]},
        {"options": [
            ["-u",  "--url",                    "<url>",               "Connect to URL"],
            ["-ts", "--tests",                  "<test>",              "Specify one or more tests to perform:"],
            ["",     "",                        "IDENT",               "Identify all cookies returned by the server with their attributes"],
            ["",     "",                        "SECURE",              "Check if secure flag is present"],
            ["",     "",                        "HTTPONLY",            "Check if HttpOnly flag is present"],
            ["",     "",                        "SAMESITE",            "Check if SameSite flag is set to Lax or Strict"],
            ["",     "",                        "PREFIX",              "Check if cookie has __Host- prefix"],
            ["",     "",                        "DOMAIN",              "Check if cookie domain is not overscoped"],
            ["",     "",                        "TECHNAME",            "Check if cookie name reveals technology"],
            ["",     "",                        "TECHFORM",            "Check if cookie value format reveals technology"],
            ["",     "",                        "ACCVAL",              "Check if server accepts arbitrary cookie values"],
            ["",     "",                        "ACCURL",              "Check if server sets cookie from URL parameter"],
            ["",     "",                        "FPD",                 "Check if empty or invalid value triggers FPD"],
            ["", "", "", ""],
            ["-c", "--cookie-name",             "<cookie-name>",       "Parse only specific <cookie-name>"],
            ["-T",  "--timeout",                "<timeout>",           "Set timeout (defaults to 10)"],
            ["-a",  "--user-agent",             "<user-agent>",        "Set User-Agent header"],
            ["-H",  "--headers",                "<header:value>",      "Set custom header(s)"],
            ["-p",  "--proxy",                  "<proxy>",             "Set proxy (e.g. http://127.0.0.1:8080)"],
            ["-l",  "--list-cookies-only",      "<list-cookies-only>", "Return cookies without vulnerabilities"],
            ["-C",  "--cache",                  "",                    "Cache requests (load from tmp in future)"],
            ["-v",  "--version",                "",                    "Show script version and exit"],
            ["-h",  "--help",                   "",                    "Show this help message and exit"],
            ["-j",  "--json",                   "",                    "Output in JSON format"],
        ]
        }]


def parse_args():
    available_tests = ["IDENT", "SECURE", "HTTPONLY", "SAMESITE", "PREFIX", "DOMAIN", "TECHNAME", "TECHFORM", "ACCVAL", "ACCURL", "FPD"]
    parser = argparse.ArgumentParser(add_help="False")
    parser.add_argument("-u",      "--url",               type=str, required=True)
    parser.add_argument("-ts", "--tests",          type=lambda s: s.upper(), nargs="+", default=available_tests)
    parser.add_argument("-c",      "--cookie-name",       type=str)
    parser.add_argument("-p",      "--proxy",             type=str)
    parser.add_argument("-l",      "--list-cookies-only", action="store_true")
    parser.add_argument("-a",      "--user-agent",        type=str, default="Penterep Tools")
    parser.add_argument("-T",      "--timeout",           type=int, default=10)
    parser.add_argument("-H",      "--headers",           type=ptmisclib.pairs, nargs="+")
    parser.add_argument("-j",      "--json",              action="store_true")
    parser.add_argument("-C",      "--cache",             action="store_true")
    parser.add_argument("-v",      "--version",           action="version", version=f"{SCRIPTNAME} {__version__}")

    parser.add_argument("--socket-address",          type=str, default=None)
    parser.add_argument("--socket-port",             type=str, default=None)
    parser.add_argument("--process-ident",           type=str, default=None)

    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        ptprinthelper.help_print(get_help(), SCRIPTNAME, __version__)
        sys.exit(0)

    args = parser.parse_args()
    args.headers = ptnethelper.get_request_headers(args)
    args.proxy = {"http": args.proxy, "https": args.proxy} if args.proxy else None

    args.timeout = args.timeout if not args.proxy else None
    ptprinthelper.print_banner(SCRIPTNAME, __version__, args.json)
    return args


def main():
    global SCRIPTNAME
    SCRIPTNAME = "ptcookiechecker"
    requests.packages.urllib3.disable_warnings()
    args = parse_args()
    script = PtCookieChecker(args)
    script.run(args)


if __name__ == "__main__":
    main()
