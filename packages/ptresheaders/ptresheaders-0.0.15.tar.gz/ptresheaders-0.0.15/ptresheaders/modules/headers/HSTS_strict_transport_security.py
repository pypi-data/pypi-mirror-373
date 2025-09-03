import re
from modules.headers._header_test_base import HeaderTestBase
from ptlibs.ptprinthelper import ptprint

class StrictTransportSecurity(HeaderTestBase):
    """
    A parser for the HTTP Strict Transport Security (HSTS) header.

    This class is responsible for parsing the `Strict-Transport-Security` header, extracting its components
    (`max-age`, `includeSubDomains`, and `preload`), and printing results based on the parsed values.

    Attributes:
        header_value (str): The value of the `Strict-Transport-Security` header to be parsed.
        attribs (dict): A dictionary containing the parsed components of the HSTS header.
    """

    def test_header(self, header_value: str):
        """
        Parses the `Strict-Transport-Security` header value and extracts the components: `max-age`,
        `includeSubDomains`, and `preload`. Calls `_print_result` to output the results.

        This method uses regular expressions to search for the presence of these components in
        the header value and updates the `attribs` dictionary accordingly.

        It also checks if the `max-age` is within a valid range and handles the `includeSubDomains`
        and `preload` attributes.

        :returns: None
        """

        # Regular expressions for HSTS header parameters
        max_age_pattern = re.compile(r'max-age=(\d+)')
        include_subdomains_pattern = re.compile(r'includeSubDomains')
        preload_pattern = re.compile(r'preload')

        self.attribs = {"max-age": None, "includeSubDomains": None, "preload": None}

        # Extracting max-age if present
        max_age_match = max_age_pattern.search(header_value)
        if max_age_match:
            max_age = int(max_age_match.group(1))
            self.attribs["max-age"] = max_age

        # Checking for includeSubDomains and preload
        self.attribs["includeSubDomains"] = bool(include_subdomains_pattern.search(header_value))
        self.attribs["preload"] = bool(preload_pattern.search(header_value))

        if not self.attribs["preload"]:
            self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-HSTSPL")
        if not self.attribs["includeSubDomains"]:
            self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-HSTSSD")

        self._print_result()

    def _print_result(self):
        """
        Prints the results of parsing the `Strict-Transport-Security` header.

        This method iterates through the parsed components (`max-age`, `includeSubDomains`, `preload`)
        and prints their respective values, along with a message indicating whether they are valid
        or not, using a bullet type for each.

        :returns: None
        """
        ptprint("Attributes:", bullet_type="TEXT", condition=not self.args.json, indent=4)
        for key, value in self.attribs.items():
            if key == "max-age" and value is not None:
                # Determine the bullet type and message for max-age
                bullet_type, message = self._get_max_age_bullet_type(value)
                result_string = f"{key}={value} {message}"
                ptprint(result_string, bullet_type=bullet_type, condition=not self.args.json, indent=8)

            elif key in ["includeSubDomains", "preload"]:
                if value:
                    ptprint(f"{key}", bullet_type="OK", condition=not self.args.json, indent=8)
                else:
                    ptprint(f"{key} (missing)", bullet_type="VULN", condition=not self.args.json, indent=8)

    def _get_max_age_bullet_type(self, value: int) -> tuple:
        """
        Determines the bullet type and message for the `max-age` value.

        This method checks the value of `max-age` and categorizes it into one of the following
        bullet types:
        - "VULN" if the value is too small (< 2592000 seconds)
        - "WARNING" if the value is between 2592000 and 31536000 seconds
        - "NOTVULN" if the value is greater than or equal to 31536001 seconds

        :param value: The `max-age` value to be checked.
        :type value: int
        :returns: A tuple containing the bullet type and a message string.
        :rtype: tuple
        """

        if value < 2592000:
            self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-HSTSINV")
            return "VULN", "(too small value, recommended value least 31536000)"
        elif value < 31536000:
            self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-HSTSINV")
            return "WARNING", "(recommended value least 31536000)"
        else:
            return "NOTVULN", ""
