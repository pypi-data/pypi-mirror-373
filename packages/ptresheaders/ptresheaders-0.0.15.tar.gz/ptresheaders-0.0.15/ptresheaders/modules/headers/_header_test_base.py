from ptlibs.ptprinthelper import ptprint, out_if, get_colored_text

class HeaderTestBase:
    """
    Base class for testing response headers.

    This class provides common functionality for testing response headers. Specific header tests
    should inherit from this base class and implement the `test_header` method.
    """

    def __init__(self, ptjsonlib, args, header_name, header_value, response, is_duplicate):
        """
        Initialize the base class for header tests.

        :param ptjsonlib: The library or object used for JSON output.
        :type ptjsonlib: Any
        :param args: Arguments or configuration options for the test.
        :type args: Any
        :param header_name: The name of the HTTP header being tested.
        :type header_name: str
        :param header_value: The value of the HTTP header being tested.
        :type header_value: str
        """
        self.ptjsonlib = ptjsonlib
        self.args = args
        self.header_name = header_name
        self.header_value = header_value
        self.response = response
        ptprint(f"{header_name}:", "INFO", not self.args.json, colortext=True, newline_above=True)
        if is_duplicate:
            ptprint(get_colored_text("Duplicate header", "WARNING"), "TEXT", condition=not self.args.json, indent=4)
        ptprint(f"{self.header_name}: {self.header_value}", "ADDITIONS", not self.args.json, colortext=True, indent=4)


    def test_header(self):
        raise NotImplementedError("Not implemented")