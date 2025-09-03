from modules.headers._header_test_base import HeaderTestBase
from ptlibs.ptprinthelper import ptprint

import re

class ContentType(HeaderTestBase):
    def test_header(self, header_value: str):
        header_values_list: list = header_value.split(", ")
        mime_type = self.get_mime_type(header_value)
        ptprint("Values:", "TEXT", not self.args.json, indent=4)
        ptprint(mime_type, bullet_type="OK" if self.is_valid_mime_type else "VULN", condition=not self.args.json, indent=8)

        charset = self.get_charset(header_value)
        if charset:
            ptprint(charset, bullet_type="OK", condition=not self.args.json, indent=8)
        else:
            ptprint("Missing charset", bullet_type="VULN", condition=not self.args.json, indent=8)

    def is_valid_mime_type(self, mime_type) -> bool:
        return True if len(mime_type.split("/")) == 2 else False

    def get_mime_type(self, string: str):
        return string.split("; ")[0]

    def get_charset(self, string: str):
        match = re.search(r"(charset=)([^;]+)", string, re.IGNORECASE)
        return ''.join(match.groups()) if match else ""