from modules.headers._header_test_base import HeaderTestBase
from ptlibs.ptprinthelper import ptprint
from ptlibs.parsers.http_request_parser import HttpRequestParser


class ContentSecurityPolicy(HeaderTestBase):

    UNSAFE_VALUES = [
        ["*", "ERROR", "PT-WEB-CODE1"],
        ["'unsafe-inline'", "ERROR", "PT-WEB-CODE1"],
        ["'unsafe-eval'", "ERROR", "PT-WEB-CODE1"],
        ["data:", "ERROR", "PT-WEB-CODE1"],
        ["blob:", "WARNING", "PT-WEB-CODE1"],
        ["http:", "ERROR", "PT-WEB-CODE1"],
        ["https:", "ERROR", "PT-WEB-CODE1"],
    ]


    def test_header(self, header_value: str):
        """
        Tests the provided header value for compliance with the Content Security Policy.

        :param header_value: The CSP header value to be tested.
        :type header_value: str
        """
        response_directives = self._parse_directives(header_value)

        self.printed_policy_definition: bool = False
        self.print_directives(response_directives, "missing")
        self.print_directives(response_directives, "default-src")
        self.print_directives(response_directives, "fetch")
        self.print_directives(response_directives, "other")
        self.print_directives(response_directives, "policy-uri")


    def print_directives(self, csp_dict: dict, directive_type: str):
        """
        Prints directives from a Content Security Policy (CSP) dictionary based on the specified type.

        Depending on the directive type, this function identifies and prints missing directives,
        `default-src` configuration, fetch directives, or other directives in the given CSP.

        :param csp_dict:
            A dictionary representing the CSP policy, where keys are directive names and values are lists of sources.
        :type csp_dict: dict

        :param directive_type:
            Specifies the type of directives to print. Can be one of the following:
            - `"missing"`: Prints directives that are missing from the policy.
            - `"default-src"`: Prints the `default-src` directive if it exists and its associated values.
            - `"fetch"`: Prints fetch-related directives, excluding `default-src`, if they exist in the policy.
            - `"other"`: Prints other types of directives defined in the CSP.
        :type directive_type: str

        :raises ValueError:
            If an invalid `directive_type` is passed.

        **Behavior:**
            - `"missing"`:
                Collects missing fetch directives and other unsupported directives, then prints them
                along with their vulnerability tags.

            - `"default-src"`:
                Prints the `default-src` directive and its values. If `default-src` is missing, it skips execution.

            - `"fetch"`:
                Prints fetch directives (e.g., `script-src`, `img-src`) found in the policy,
                unless `default-src` is defined.

            - `"other"`:
                Prints non-fetch directives found in the policy (e.g., `sandbox`, `upgrade-insecure-requests`).
        """
        missing_fetch_directives: list = [key for d in self.get_missing_fetch_directives(csp_dict) for key in d.keys()]
        missing_all_directives: list = []
        missing_all_directives: list = missing_fetch_directives if not "default-src" in csp_dict else missing_all_directives
        missing_all_directives += self.get_others_directives(csp_dict)

        if missing_all_directives:
            self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-CSPINV")

        if directive_type == "missing":
            ptprint("Missing directives:", "", not self.args.json, indent=4)
            for key in missing_all_directives:
                #self.ptjsonlib.add_vulnerability(f"MISSING-DIRECTIVE-{key}")
                ptprint(key, "VULN", not self.args.json, indent=8)

        if directive_type == "default-src":
            if not "default-src" in csp_dict:
                return
            ptprint(f"Policy definition:", "", condition=not self.args.json and (not self.printed_policy_definition), newline_above=True, indent=4)
            ptprint('default-src', "", not self.args.json, indent=8)
            for key in missing_fetch_directives:
                ptprint(key, "", not self.args.json, indent=12)
            self._print_values("", csp_dict.get("default-src", []))
            self.printed_policy_definition = True

        if directive_type == "fetch":
            ptprint(f"Policy definition:", "", condition=not self.args.json and (not self.printed_policy_definition), newline_above=True, indent=4)
            for key, value_list in csp_dict.items():
                if key in self._get_all_exists_fetch_directives():
                    if key == "default-src":
                        continue
                    self._print_values(key, value_list)
            self.printed_policy_definition = True

        if directive_type == "other":
            ptprint(f"Policy definition:", "", condition=not self.args.json and (not self.printed_policy_definition), newline_above=True, indent=4)
            for key, value_list in csp_dict.items():
                if key in self._get_all_exists_other_directives():
                    self._print_values(key, value_list)
            self.printed_policy_definition = True

        if directive_type == "unstandard":
            keys_to_remove = self._get_all_exists_fetch_directives() + self._get_all_exists_other_directives()
            for key in keys_to_remove:
                if key in csp_dict:
                    csp_dict.pop(key)

            if csp_dict.keys():
                ptprint("Non-standard directives:", "", not self.args.json, newline_above=True, indent=4)
                for key, value_list in csp_dict.items():
                    self._print_values(key, value_list)

        if directive_type == "policy-uri":
            if "policy-uri" in csp_dict.keys():
                ptprint("Policy-Uri:", "", not self.args.json, newline_above=True, indent=4)
                # TODO: Add-Vulnerability
                for value in csp_dict["policy-uri"]:
                    ptprint(value, "", not self.args.json, indent=8)
                ptprint("Deprecated directive", "WARNING", not self.args.json, indent=8)

    def _print_values(self, key, value_list, indent=8):
        """Helper method to print sorted values with vulnerability checks."""
        if not any(value_list):

            if key in ["upgrade-insecure-requests"]:
                ptprint(key, "OK", not self.args.json and key, newline_above=False, indent=indent)
            else:
                ptprint(key, "WARNING", not self.args.json and key, newline_above=False, indent=indent)
                ptprint(f"Null value", "WARNING", not self.args.json, indent=indent+4)
            return
        else:
            ptprint(key, "", not self.args.json and key, newline_above=False, indent=indent)
            for value in sorted(value_list):
                is_vuln = False
                for unsafe_string, bullet_type, json_vuln_code in self.UNSAFE_VALUES:  # Extract bullet type
                    if unsafe_string == value:
                        ptprint(value, bullet_type, not self.args.json, indent=indent+4)
                        is_vuln = True
                        break

                if value.startswith("http://"):
                    ptprint(value, "WARNING", not self.args.json, indent=indent+4)
                    continue

                if not is_vuln:
                    ptprint(value, "NOTVULN", not self.args.json, indent=indent+4)

    def get_missing_fetch_directives(self, csp_dict):
        """
        Identifies missing fetch directives in the given CSP dictionary.

        This method compares the directives in the provided `csp_dict` with all existing fetch directives.
        For each fetch directive that is missing from `csp_dict`, it adds an entry to the result.
        If `default-src` is defined in the `csp_dict`, its value is included as the fallback for the missing fetch directive.

        :param csp_dict:
            A dictionary representing the CSP policy, where keys are directive names and values are lists of sources.
        :type csp_dict: dict

        :return:
            A list of dictionaries, where each dictionary represents a missing fetch directive.
            The key is the directive name, and the value is the fallback value from `default-src` or `None`.
        :rtype: list[dict]
        """
        fetch_directives = self._get_all_exists_fetch_directives()
        result = []
        for directive in fetch_directives:
            if directive not in csp_dict:
                result.append({directive: csp_dict.get("default-src", None)})
        return result

    def get_others_directives(self, csp_dict):
        """
        Identifies missing non-fetch directives in the given CSP dictionary.

        This method compares the directives in the provided `csp_dict` with all recognized non-fetch directives.
        It returns a list of directives that are not present in the `csp_dict`.

        :param csp_dict:
            A dictionary representing the CSP policy, where keys are directive names and values are lists of sources.
        :type csp_dict: dict

        :return:
            A list of missing non-fetch directive names.
        :rtype: list[str]

        :example:
            >>> csp_dict = {
            ...     "script-src": ["'self'"]
            ... }
            >>> get_others_directives(csp_dict)
            ['sandbox', 'upgrade-insecure-requests']
        """

        others = self._get_all_exists_other_directives()
        result = []
        for directive in others:
            if directive not in csp_dict:
                result.append(directive)
        return result


    def _parse_directives(self, header_value: str) -> dict:
        """
        Parse a Content Security Policy (CSP) header string into a dictionary of directives.

        This method processes the CSP header string (usually found in the `Content-Security-Policy` HTTP
        header) and converts it into a dictionary where the keys are directive names and the values are
        lists of sources or values associated with those directives. The function also moves `default-src`
        to the first position in the resulting dictionary, if present, and removes any empty keys.

        :param header_value:
            A CSP header string to be parsed. It contains a semicolon-separated list of directives and their associated values.
        :type header_value: str

        :return:
            A dictionary mapping directive names to their corresponding values, where each value is a list of sources or tokens.
        :rtype: dict

        :example:
            >>> header_value = "default-src 'self'; script-src 'unsafe-inline'; img-src 'none'"
            >>> _parse_directives(header_value)
            {
                'default-src': ["'self'"],
                'script-src': ["'unsafe-inline'"],
                'img-src': ["'none'"]
            }
        """
        directives_map: dict = {}
        for directive in [directive.lstrip() for directive in header_value.split(";")]:
            directive = directive.lower()
            splitted = directive.split(" ", 1)
            directive_name = splitted[0]
            directive_values = splitted[1] if len(splitted) > 1 else ""
            directives_map[directive_name] = directive_values.split(" ")
        directives_map = self._move_keys_to_index(directives_map, ["default-src"], 0) # move default src as first index
        directives_map = {k: v for k, v in directives_map.items() if k} # pop keys with empty value
        return directives_map

    def _get_all_exists_other_directives(self):
        return [
            "base-uri",
            "form-action",
            "frame-ancestors",
            "report-to",
            "report-uri",
            "object-src",
            "upgrade-insecure-requests",
        ]

    def _get_all_exists_fetch_directives(self):
        return [
            "default-src",
            "child-src",
            "connect-src",
            "font-src",
            "frame-src",
            "img-src",
            "manifest-src",
            "media-src",
            "script-src",
            "script-src-elem",
            "script-src-attr",
            "style-src",
            "style-src-elem",
            "style-src-attr",
            "worker-src",
            "fenced-frame-src",
            "prefetch-src",
        ]

    def _move_keys_to_index(self, csp_dict: dict, keys_to_move: list, index: int):
        if isinstance(keys_to_move, str):
            keys_to_move = [keys_to_move]

        items_to_move = [(key, csp_dict[key]) for key in keys_to_move if key in csp_dict]
        remaining_items = [(key, value) for key, value in csp_dict.items() if key not in keys_to_move]
        reordered_items = (remaining_items[:index] + items_to_move + remaining_items[index:])
        reordered_dict = dict(reordered_items)
        return reordered_dict