from modules.headers._header_test_base import HeaderTestBase
from ptlibs.ptprinthelper import ptprint

class ReportingEndpoints(HeaderTestBase):

    def test_header(self, header_value: str):
        parsed = self.parse_values(header_value)
        for key, value in parsed.items():
            ptprint(f'{key}="{value}"', "TEXT", not self.args.json, indent=4)

    def parse_values(self, header_value):
        return {key.strip(): value.strip().strip('"') for key, value in (item.split("=", 1) for item in header_value.split(", "))}
