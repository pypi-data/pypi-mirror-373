from modules.headers._header_test_base import HeaderTestBase
from ptlibs.ptprinthelper import ptprint

class ReferrerPolicy(HeaderTestBase):
    possible_values = [
        ["no-referrer", "OK"],
        ["origin", "OK"],
        ["origin-when-cross-origin", "OK"],
        ["same-origin", "OK"],
        ["strict-origin", "OK"],
        ["strict-origin-when-cross-origin", "OK"],
        ["no-referrer-when-downgrade", "WARNING"],
        ["unsafe-url", "VULN"]
    ]

    def test_header(self, header_value: str):
        header_values_list: list = header_value.split(", ")
        ptprint("Values:", "TEXT", not self.args.json, indent=4)
        for value in header_values_list:
            bullet = self._get_bullet_type(value)
            ptprint(value, bullet_type=bullet, condition=not self.args.json, indent=8)
            if bullet == "VULN":
                self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-REFPOLINV")

    def _get_bullet_type(self, value):
        for possible_value in self.possible_values:
            if possible_value[0] == value:
                return possible_value[1]
        return "VULN"
