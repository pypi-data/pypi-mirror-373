import base64
import string
import random
import re
import urllib

from ptlibs import ptprinthelper, ptjsonlib, ptmisclib
from typing import List, Tuple
from http.cookies import SimpleCookie
import requests

try:
    from ptcookiechecker.modules.cookie_rules import COMMON_COOKIES
except ImportError:
    from modules.cookie_rules import COMMON_COOKIES


class CookieTester:

    def __init__(self):
        self.COMMON_COOKIES = COMMON_COOKIES

    def run(self, response, args, ptjsonlib: object, test_cookie_issues: bool = True, filter_cookie: str = None):
        self.args = args
        self.args.tests = getattr(args, "tests", [])
        self.ptjsonlib = ptjsonlib
        self.use_json = self.args.json
        self.node_key: str = None

        self.filter_cookie: str = filter_cookie
        self.test_cookie_issues: bool = test_cookie_issues
        self.duplicate_flags: bool = None
        self.set_cookie_list: List[str] = self._get_set_cookie_headers(response)
        self.cookie_names_list = []
        self.base_indent = 4


        if self.args.tests:
            self.test_cookie_issues = True

        # Cookie injection tests
        if self.test_cookie_issues:
            cookie_injection_from_headers: list = self.check_cookie_injection_from_headers(url=response.url)
            cookie_acceptance_from_get_params: list = self.check_cookie_acceptance_from_get_param(url=response.url)
            cookie_injection_from_get_params: list = self.check_cookie_injection_from_get_param(url=response.url) if cookie_acceptance_from_get_params else []

        # Print Set-Cookie:
        for header, value in response.raw.headers.items():
            if header.lower() == "set-cookie":
                ptprinthelper.ptprint(ptprinthelper.get_colored_text(f"Set-Cookie: {value}", "ADDITIONS"), colortext="WARNING", condition=not self.use_json, indent=(self.base_indent))

        cookie_list = response.cookies

        self._bypass_cookiejar_restrictions(response, set_cookie_list=self.set_cookie_list)

        if not cookie_list and not self.set_cookie_list:
            ptprinthelper.ptprint(f"Site returned no cookies", bullet_type="", condition=not self.use_json, indent=4)
            return



        for index, cookie in enumerate(cookie_list):

            if self.filter_cookie and (self.filter_cookie.lower() != cookie.name.lower()):
                continue

            self.cookie_names_list.append(cookie.name)

            full_cookie: str = self._find_cookie_in_headers(cookie_list=self.set_cookie_list, cookie_to_find=f"{cookie.name}={cookie.value}") or str(cookie)
            _is_custom_cookie = cookie._rest.get("isCustomCookie", False) # True if added forcefully via custom function

            self.duplicate_flags = self.detect_duplicate_attributes(full_cookie)
            cookie_max_age = self._get_max_age_from_cookie(full_cookie)
            cookie_name = f"{cookie.name}={cookie.value}"
            cookie_path = cookie.path
            cookie_domain = cookie.domain
            cookie_expiration_timestamp = self._get_expires_from_cookie(full_cookie) # cookie.expires if not _is_custom_cookie else self._get_expires_from_cookie(full_cookie)
            expires_string = next((m.group(1) for m in [re.search(r'Expires=([^;]+)', full_cookie, re.IGNORECASE)] if m), "")
            #cookie_expiration_text = next((item.split('=')[1] for item in full_cookie.split(":", maxsplit=1)[-1].strip().lower().split('; ') if item.lower().startswith('expires=')), None)

            cookie_secure_flag = cookie.secure
            cookie_http_flag = bool("httponly" in (key.lower() for key in cookie._rest.keys()))
            cookie_samesite_flag = next((value for key, value in cookie._rest.items() if key.lower() == "samesite"), None)

            if "IDENT" in self.args.tests:
                node = self.ptjsonlib.create_node_object(
                    "cookie",
                    properties={
                        "name": cookie.name,
                        "is_web_cookie_secure_flag": cookie_secure_flag,
                        "is_web_cookie_http_only_flag": cookie_http_flag,
                        "web_cookie_same_site_flag": cookie_samesite_flag.lower() if cookie_samesite_flag else False,
                        "path": cookie_path,
                        "domain": cookie_domain,
                        "description": full_cookie
                    },
                    vulnerabilities=[]
                )

                if self.filter_cookie:
                    self.node_key = node["key"]
                self.ptjsonlib.add_node(node)

            ptprinthelper.ptprint(f'Name:   {ptprinthelper.get_colored_text(cookie.name, "TITLE")}', condition=not self.use_json, newline_above=True if index > 0 else False, indent=self.base_indent)

            if self.test_cookie_issues:
                if "TECHNAME" in self.args.tests:
                    self.check_cookie_name(cookie.name)

                if "PREFIX" in self.args.tests:
                    self.check_host_prefix(cookie.name)

            ptprinthelper.ptprint(f"Value:  {urllib.parse.unquote(cookie.value)}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)
            if self.is_base64(urllib.parse.unquote(cookie.value)):
                ptprinthelper.ptprint(f"Decoded value: {repr(self.is_base64(urllib.parse.unquote(cookie.value)))[2:-1]}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)

            if self.test_cookie_issues:
                if "TECHFORM" in self.args.tests:
                    self.check_cookie_value(urllib.parse.unquote(cookie.value))

                if "ACCVAL" in self.args.tests:
                    if cookie.name in cookie_injection_from_headers:
                        ptprinthelper.ptprint(f"Application accepts any value from cookie", bullet_type="WARNING", condition=not self.use_json, indent=(self.base_indent+4))
                        vuln_code = "PTV-WEB-LSCOO-REFUSE"
                        self.ptjsonlib.add_vulnerability(vuln_code, node_key=self.node_key)

                if "ACCURL" in self.args.tests:
                    vuln_code = "PTV-WEB-LSCOO-URLSET"
                    if cookie.name in cookie_acceptance_from_get_params:
                        ptprinthelper.ptprint(f"Application accepts cookie value from GET parameter", bullet_type="WARNING", condition=not self.use_json, indent=(self.base_indent+4))
                        self.ptjsonlib.add_vulnerability(vuln_code, node_key=self.node_key)
                    if cookie.name in cookie_injection_from_get_params:
                        ptprinthelper.ptprint(f"Application sets any value passed in GET parameter into the cookie ", bullet_type="WARNING", condition=not self.use_json, indent=(self.base_indent+4))
                        self.ptjsonlib.add_vulnerability(vuln_code, node_key=self.node_key)

            ptprinthelper.ptprint(f"Domain: {cookie_domain}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)

            if self.test_cookie_issues:
                if "DOMAIN" in self.args.tests:
                    self.check_cookie_domain(cookie_domain)

            ptprinthelper.ptprint(f"Path:   {cookie_path}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)
            ptprinthelper.ptprint(f"Expires:{expires_string if expires_string else cookie_expiration_timestamp}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)
            if cookie_max_age:
                ptprinthelper.ptprint(f"Max-Age:{cookie_max_age}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)

            ptprinthelper.ptprint(f"Flags: ", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)
            if self.test_cookie_issues:
                if "SAMESITE" in self.args.tests:
                    self.check_cookie_samesite_flag(cookie_samesite_flag)

                if "SECURE" in self.args.tests:
                    self.check_cookie_secure_flag(cookie_secure_flag)

                if "HTTPONLY" in self.args.tests:
                    self.check_cookie_httponly_flag(cookie_http_flag)
            else:
                ptprinthelper.ptprint(f"    SameSite: {cookie_samesite_flag}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)
                ptprinthelper.ptprint(f"    Secure: {cookie_secure_flag}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)
                ptprinthelper.ptprint(f"    HttpOnly: {cookie_http_flag}", bullet_type="TEXT", condition=not self.use_json, indent=self.base_indent)

            if "FPD" in self.args.tests:
                self._test__fpd_via_cookie_injection(self.args.url)


    def detect_duplicate_attributes(self, cookie_string):
        attributes = [attr.strip() for attr in cookie_string.split(';')]
        attribute_counts = {}
        for attr in attributes:
            key = attr.split('=')[0].strip().lower()  # Get the attribute name, case-insensitive
            attribute_counts[key] = attribute_counts.get(key, 0) + 1
        duplicates = {key.lower(): count for key, count in attribute_counts.items() if count > 1}
        return list(duplicates.keys())

    def _find_cookie_in_headers(self, cookie_list: list, cookie_to_find: str):
        for cookie in cookie_list:
            if re.findall(re.escape(cookie_to_find), cookie):
                return cookie

    def _get_set_cookie_headers(self, response):
        """Returns Set-Cookie headers from <response.raw.headers>"""
        raw_cookies: list = []
        if [h for h in response.raw.headers.keys() if h.lower() == "set-cookie"]:
            for header, value in response.raw.headers.items():
                if header.lower() == "set-cookie":
                    raw_cookies.append(f"{header}: {value}")
        return raw_cookies

    def _find_technology_by_cookie_value(self, cookie_value: str) -> list:
        """
        Determines which technologies a given cookie value matches based on defined rules.

        The function checks the provided cookie value against predefined technology rules
        in terms of length and format. If the cookie matches the rules for a technology,
        the corresponding technology name is added to the result list.

        Args:
            cookie_value (str): The value of the cookie to be analyzed.

        Returns:
            list: A list of technology names that match the cookie value. If no match is found,
                an empty list is returned.
        """
        result: list = []
        for cookie in self.COMMON_COOKIES:
            if "rules" in cookie and "value_format" in cookie["rules"]:
                cookie_value_pattern = cookie["rules"]["value_format"]
                if re.match(cookie_value_pattern, cookie_value):
                    result.append(cookie["description"])
        return result

    def _find_technology_by_cookie_name(self, cookie_name):
        for cookie in self.COMMON_COOKIES:
            cookie_name_pattern = cookie["name"]
            if re.match(cookie_name_pattern, cookie_name, re.IGNORECASE):
                return (cookie.get("technology"), cookie["description"], "ERROR", "ERROR")
        return None

    def check_cookie_name(self, cookie_name: str):
        result = self._find_technology_by_cookie_name(cookie_name)
        if result:
            technology_name, message, json_code, bullet_type = result
            ptprinthelper.ptprint(f"Cookie has default name for {message}", bullet_type=bullet_type, condition=not self.use_json, colortext=False, indent=self.base_indent+4)
            vuln_code = "PTV-WEB-INFO-TEDEFNAME"
            self.ptjsonlib.add_vulnerability(vuln_code, node_key=self.node_key) #if args.cookie_name else node["vulnerabilities"].append({"vulnCode": vuln_code})

    def check_host_prefix(self, cookie_name: str):
        if not cookie_name.startswith("__Host-"):
            ptprinthelper.ptprint(f"Cookie is missing '__Host-' prefix", bullet_type="VULN", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
            vuln_code = "PTV-WEB-LSCOO-HOSTPREF"
            self.ptjsonlib.add_vulnerability(vuln_code, node_key=self.node_key) #if args.cookie_name else node["vulnerabilities"].append({"vulnCode": vuln_code})

    def check_cookie_value(self, cookie_value: str):
        result = self._find_technology_by_cookie_value(cookie_value)
        if result:
            vuln_code = "PTV-WEB-INFO-TEDEFFORM"
            self.ptjsonlib.add_vulnerability(vuln_code, node_key=self.node_key)
            ptprinthelper.ptprint(f"Cookie value has default format of {', '.join(result) if len(result) > 1 else result[0]}", bullet_type="VULN", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
            #self.ptjsonlib.add_vulnerability(vuln_code) if args.cookie_name else node["vulnerabilities"].append({"vulnCode": vuln_code})

    def check_cookie_domain(self, cookie_domain: str):
        if cookie_domain.startswith("."):
            vuln_code = "PTV-WEB-LSCOO-DOMAIN"
            self.ptjsonlib.add_vulnerability(vuln_code, node_key=self.node_key)
            ptprinthelper.ptprint(f"Overscoped cookie issue", bullet_type="WARNING", condition=not self.use_json, colortext=False, indent=self.base_indent+4)

    def check_cookie_httponly_flag(self, cookie_http_flag):
        if not cookie_http_flag:
            vuln_code = "PTV-WEB-LSCOO-FLHTTP"
            self.ptjsonlib.add_vulnerability(vuln_code, node_key=self.node_key) #if args.cookie_name else node["vulnerabilities"].append({"vulnCode": vuln_code})
            ptprinthelper.ptprint(f"HttpOnly flag missing", bullet_type="VULN", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
        else:
            if "httponly" in self.duplicate_flags:
                ptprinthelper.ptprint(f"HttpOnly flag duplicate", bullet_type="WARNING", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
            else:
                ptprinthelper.ptprint(f"HttpOnly flag present", bullet_type="OK", condition=not self.use_json, colortext=False, indent=self.base_indent+4)

    def check_cookie_samesite_flag(self, cookie_samesite_flag):
        if not cookie_samesite_flag:
            vuln_code = "PTV-WEB-LSCOO-FLSAME"
            self.ptjsonlib.add_vulnerability(vuln_code, node_key=self.node_key) # if args.cookie_name else node["vulnerabilities"].append({"vulnCode": vuln_code})
            ptprinthelper.ptprint(f"SameSite flag missing", bullet_type="VULN", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
        else:
            if "samesite" in self.duplicate_flags:
                ptprinthelper.ptprint(f"SameSite duplicate", bullet_type="WARNING", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
            else:
                _bullet = "OK" if not cookie_samesite_flag.lower() == "none" else "WARNING"
                ptprinthelper.ptprint(f"SameSite={cookie_samesite_flag}", bullet_type=_bullet, condition=not self.use_json, colortext=False, indent=self.base_indent+4)

    def check_cookie_secure_flag(self, cookie_secure_flag):
        if not cookie_secure_flag:
            vuln_code = "PTV-WEB-LSCOO-FLSEC"
            self.ptjsonlib.add_vulnerability(vuln_code, node_key=self.node_key) #if args.cookie_name else node["vulnerabilities"].append({"vulnCode": vuln_code})
            ptprinthelper.ptprint(f"Secure flag missing", bullet_type="VULN", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
        else:
            if "secure" in self.duplicate_flags:
                ptprinthelper.ptprint(f"Secure flag duplicate", bullet_type="WARNING", condition=not self.use_json, colortext=False, indent=self.base_indent+4)
            else:
                ptprinthelper.ptprint(f"Secure flag present", bullet_type="OK", condition=not self.use_json, colortext=False, indent=self.base_indent+4)

    def is_base64(self, value):
        try:
            if isinstance(value, str) and re.match('^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$', value): # Kontrola, zda hodnota odpovídá formátu Base64
                decoded_value = base64.b64decode(value, validate=True)
                # Check if the decoded value is binary (contains non-printable characters)
                if all(c in string.printable for c in decoded_value.decode('utf-8', errors='ignore')):
                    return decoded_value  # Return the decoded value if it's printable
                else:
                    return None  # Return None if the result is binary (non-printable)
        except (base64.binascii.Error, TypeError):
            return False

    def check_cookie_injection_from_headers(self, url: str):
        """
        Tests if the application accepts arbitrary values in cookies.

        This method:
        1. Takes the cookies from a previous response and generates random values for each cookie, preserving the original cookie length.
        2. Sends a new request to the same URL, but with the modified cookies (random values).
        3. Compares the cookies from the new response to the original set of cookies.

        If any of the original cookies are missing in the response after sending random values,
        it indicates that the server accepted the random cookie values.
        """

        extracted_cookies: List[Tuple] = self._extract_cookie_names_and_values(set_cookie_list=self.set_cookie_list)
        cookies_to_send = {cookie[0]: ''.join(random.choices(string.ascii_letters+string.digits, k=len(cookie[1]) if len(cookie[1]) >= 1 else 10)) for cookie in extracted_cookies}
        response = requests.get(url=url, cookies=cookies_to_send, headers=self.args.headers, proxies=self.args.proxy, verify=False, allow_redirects=False)

        cookies_list1 = [cookie[0] for cookie in extracted_cookies]
        cookies_list2 = [cookie[0] for cookie in self._extract_cookie_names_and_values(self._get_set_cookie_headers(response))]
        missing_cookies = [cookie for cookie in cookies_list1 if cookie not in cookies_list2]
        return missing_cookies

    def check_cookie_acceptance_from_get_param(self, url) -> list:
        """Check if the application accepts cookie values passed via GET parameters."""
        extracted_cookies = self._extract_cookie_names_and_values(set_cookie_list=self.set_cookie_list)
        cookies_to_send = {cookie_name: cookie_value for cookie_name, cookie_value in extracted_cookies}

        # Send request with cookies in GET query
        response = requests.get(url, params=cookies_to_send, headers=self.args.headers, proxies=self.args.proxy, verify=False, allow_redirects=False)
        response_cookie_names = [c[0] for c in self._extract_cookie_names_and_values(self._get_set_cookie_headers(response))]
        vuln_cookies = [cookie_name for cookie_name, _ in extracted_cookies if cookie_name not in response_cookie_names]
        return vuln_cookies

    def check_cookie_injection_from_get_param(self, url) -> list:
        """Check if the application sets cookie values passed via GET parameters into the response."""
        extracted_cookies = self._extract_cookie_names_and_values(set_cookie_list=self.set_cookie_list)
        cookies_to_send = {cookie_name: ''.join(random.choices(string.ascii_letters + string.digits, k=len(cookie_value) if len(cookie_value) >= 1 else 10)) for cookie_name, cookie_value in extracted_cookies}

        # Send request with cookies in GET query
        response = requests.get(url, params=cookies_to_send, proxies=self.args.proxy, verify=False, allow_redirects=False)
        response_cookies = self._extract_cookie_names_and_values(self._get_set_cookie_headers(response))

        vuln_cookies = [cookie_name for cookie_name, cookie_value in response_cookies if cookie_value == cookies_to_send.get(cookie_name)]
        return vuln_cookies


    def _get_all_cookie_names(self, set_cookie_list: list) -> list:
        """Returns list of all cookie names parsed from response headers."""
        return [re.match(r"set-cookie: (\S+)=.*", header, re.IGNORECASE).group(1) for header in set_cookie_list if re.match(r"set-cookie: (\S+)=.*", header, re.IGNORECASE)]

    def _extract_cookie_names_and_values(self, set_cookie_list: list) -> List[Tuple[str, str]]:
        """Returns a list of tuples containing cookie names and their corresponding values parsed from response headers."""
        return [(match.group(1), match.group(2)) for header in set_cookie_list if (match := re.match(r"set-cookie: (\S+?)=([^;]*)", header, re.IGNORECASE))]

    def repeat_with_max_len(self, base_string="foobar", max_len=40):
        # Repeat the base string enough times to exceed the max length
        repeated = (base_string * (max_len // len(base_string))) + base_string[:max_len % len(base_string)]
        return repeated


    def _bypass_cookiejar_restrictions(self, response, set_cookie_list) -> None:
        """
        Adds cookies to the response's CookieJar, bypassing standard restrictions.

        This function ensures that cookies, which would typically be excluded due
        to conditions such as `Max-Age=0` are forcefully added to the provided response's CookieJar.
        """

        for cookie_name, cookie_value in self._extract_cookie_names_and_values(set_cookie_list=self.set_cookie_list):
            # Check if this cookie is not in response.cookies
            if not any(f"{cookie_name}={cookie_value}" in str(cookie) for cookie in response.cookies):
                full_cookie: str = self._find_cookie_in_headers(cookie_list=self.set_cookie_list, cookie_to_find=f"{cookie_name}={cookie_value}") or str(cookie)
                full_cookie: str = re.sub(r"SameSite(?!=[\w-]+)", "SameSite=_PLACEHOLDER", full_cookie, flags=re.IGNORECASE)
                full_cookie: str = re.sub(r"set-cookie:", "", full_cookie, flags=re.IGNORECASE).lstrip()

                simple_cookie = SimpleCookie(full_cookie)
                for key, morsel in simple_cookie.items():
                    _rest = {"isCustomCookie": True} # Add custom flag for Expires extraction.
                    httponly = morsel.get("httponly")
                    samesite = morsel.get("samesite")
                    if httponly:
                        _rest.update({"HttpOnly": None})
                    if samesite:
                        if samesite == "_PLACEHOLDER":
                            _rest.update({"SameSite": None}) # default behaviour if no value provided. SimpleCookie wont be without attribute so we use temporary placeholder.
                        else:
                            _rest.update({"SameSite": samesite})

                    cookie_obj = requests.cookies.create_cookie(
                        name=key,
                        value=morsel.value,
                        path=morsel['path'] if morsel['path'] else "/",
                        domain=morsel.get("domain") if morsel.get("domain") else response.url.split("//", 1)[-1].split("/")[0],
                        secure=morsel.get("secure", False),
                        rest=_rest
                    )

                    response.cookies.set_cookie(cookie_obj)


    def _get_max_age_from_cookie(self, full_cookie):
        _max_age_match = re.search(r"max-age.*?=(.*?);", full_cookie, re.IGNORECASE)
        cookie_max_age = _max_age_match.groups()[0] if _max_age_match else None
        try:
            cookie_max_age = int(cookie_max_age)
            cookie_max_age = f"{cookie_max_age} ({round(cookie_max_age/86400)} days)"
            return cookie_max_age
        except:
            return cookie_max_age

    def _get_expires_from_cookie(self, full_cookie):
        _expires = re.search(r"expires.*?=(.*?);", full_cookie, re.IGNORECASE)
        cookie_expires = _expires.groups()[0] if _expires else ""
        return cookie_expires

    def _test__fpd_via_cookie_injection(self, url: str) -> None:
        """
        Test for potential Full Path Disclosure (FPD) by sending
        malformed cookies and checking the server's response.

        - Sends a cookie with an empty value.
        - Sends a cookie with invalid characters (semicolon inside value).
        - Searches response body for error messages indicating FPD.
        """
        # Define test templates
        test_templates = {
            "FPD detected when cookie value is empty": "",
            "FPD detected when cookie value contains invalid characters": "aaa;bbb",
        }

        # Build test cases for each cookie name
        test_cases = {}
        for name in self.cookie_names_list:
            for title, value in test_templates.items():
                key = f"{title}_{name}"
                test_cases[key] = {"cookie": {name: value}, "title": title}

        # Error patterns to detect FPD
        error_patterns = [
            r"<b>Warning</b>: .* on line.*",
            r"<b>Fatal error</b>: .* on line.*",
            r"<b>Error</b>: .* on line.*",
            r"<b>Notice</b>: .* on line.*",
        ]

        fpd_findings = {}

        # Execute test cases
        for case_name, data in test_cases.items():
            cookies = data["cookie"]
            title = data["title"]

            try:
                headers_with_cookie = dict(self.args.headers or {})
                cookie_header_value = "; ".join(f"{k}={v}" for k, v in cookies.items())
                headers_with_cookie["Cookie"] = cookie_header_value

                response, dump = ptmisclib.load_url_from_web_or_temp(
                    url,
                    method="GET",
                    headers=headers_with_cookie,
                    proxies=self.args.proxy,
                    timeout=self.args.timeout,
                    redirects=False,
                    verify=False,
                    cache=self.args.cache,
                    dump_response=True,
                )

                # Check against error patterns
                if any(re.search(pattern, response.text, re.IGNORECASE) for pattern in error_patterns):
                    fpd_findings.setdefault(title, []).append((cookies, dump))

            except requests.RequestException:
                # Skip if the server rejects the request
                continue

        # Print grouped findings (title only once)
        for title, results in fpd_findings.items():
            ptprinthelper.ptprint(" ", bullet_type="TEXT", condition=not self.use_json)
            ptprinthelper.ptprint(
                title,
                bullet_type="TITLE",
                condition=not self.use_json,
                colortext=True,
            )
            for cookies, dump in results:
                note = f"Vulnerable cookie: {cookies}"
                self.ptjsonlib.add_vulnerability(
                    vuln_code="PTV-WEB-FPD-COOKIE",
                    note=note,
                    vuln_request=dump["request"],
                    vuln_response=dump["response"],
                    node_key=self.node_key
                )
                ptprinthelper.ptprint(
                    note,
                    bullet_type="TEXT",
                    condition=not self.use_json,
                )
