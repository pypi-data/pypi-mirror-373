from modules.headers._header_test_base import HeaderTestBase
from ptlibs.ptprinthelper import ptprint

class XDNSPrefetchControl(HeaderTestBase):
    def test_header(self, header_value: str):
        ptprint("Values:", "TEXT", not self.args.json, indent=4)
        if header_value.lower() in ["on", "off"]:
            ptprint(header_value, "OK", not self.args.json, indent=8)
        else:
            ptprint(f"{header_value}", "VULN", not self.args.json, indent=8)
            self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-XDPCINV")
