from modules.headers._header_test_base import HeaderTestBase
from ptlibs.ptprinthelper import ptprint

class XFrameOptions(HeaderTestBase):
    """
    A test class for validating the 'X-Frame-Options' header.

    This class tests the `X-Frame-Options` header, ensuring that it is set to valid values like
    `DENY` or `SAMEORIGIN`. It also handles the `ALLOW-FROM` value, parsing and printing
    the domains specified with that directive. The header value is checked for validity and
    appropriate messages are printed based on the result.

    Inherited from:
        :class:`HeaderTestBase`: The base class that provides common functionality for header tests.

    Attributes:
        header_value (str): The value of the `X-Frame-Options` header to be tested.
        args (Namespace): Command line arguments, including whether to output in JSON format.

    Methods:
        test_header():
            Runs the test for the `X-Frame-Options` header, checking if the value is valid
            and printing corresponding results.
    """

    def test_header(self, header_value: str):
        """
        Test the 'X-Frame-Options' header value.

        This method checks the `X-Frame-Options` header value against valid options such as
        'DENY', 'SAMEORIGIN', and 'ALLOW-FROM'. It processes the header value and prints
        corresponding messages. If the value is `ALLOW-FROM`, it extracts and prints the allowed
        domains. For invalid values, an error message is displayed.

        The following cases are handled:
        - If the value is 'DENY' or 'SAMEORIGIN', it prints the value as valid.
        - If the value is 'ALLOW-FROM', it lists the domains allowed in the iframe.
        - For any other value, it marks the header as invalid and prints an error.

        Output:
            Prints results using :func:`ptprint`, with different colors and indentation based on the outcome.

        Returns:
            None
        """
        ptprint("Values:", "TEXT", not self.args.json, indent=4)

        header_value_list = header_value.split(" ")

        if header_value_list[0].upper() in ['DENY', 'SAMEORIGIN']:
            ptprint(header_value, "OK", not self.args.json, indent=8)

        elif header_value_list[0].upper() in ["ALLOW-FROM"]:
            allow_from_values = header_value_list[1:]
            ptprint(f"ALLOW-FROM", "WARNING", not self.args.json, indent=8)
            self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-FRAMEINV")
            for key in allow_from_values:
                ptprint(key, "TEXT", not self.args.json, indent=12)

        else:
            ptprint(f"{header_value} (value is not valid)", "ERROR", not self.args.json, indent=8)
            self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-FRAMEINV")