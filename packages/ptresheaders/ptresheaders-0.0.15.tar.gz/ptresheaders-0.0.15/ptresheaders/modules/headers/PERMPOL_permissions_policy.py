from modules.headers._header_test_base import HeaderTestBase
from ptlibs.ptprinthelper import ptprint

class PermissionsPolicy(HeaderTestBase):

    standardized_permissions: list = [
        "accelerometer",
        "ambient-light-sensor",
        "autoplay",
        "battery",
        "camera",
        "cross-origin-isolated",
        "display-capture",
        "document-domain",
        "encrypted-media",
        "execution-while-not-rendered",
        "execution-while-out-of-viewport",
        "fullscreen",
        "geolocation",
        "gyroscope",
        "keyboard-map",
        "magnetometer",
        "microphone",
        "midi",
        "navigation-override",
        "payment",
        "picture-in-picture",
        "publickey-credentials-get",
        "screen-wake-lock",
        "sync-xhr",
        "usb",
        "web-share",
        "xr-spatial-tracking",
    ]

    def test_header(self, header_value: str):
        """
        Tests the provided header value for compliance with the Content Security Policy.

        :param header_value: The CSP header value to be tested.
        :type header_value: str
        """
        response_permissions_list: list = self._parse_permissions(header_value)
        missing_permissions: list = [p for p in self.standardized_permissions if p not in [j.split("=")[0] for j in response_permissions_list]]

        # TODO: Kontrolovat obsah direktiv
        #   Pokud je obsah direktivy *, vypsat warning
        self._print_permissions("Values", sorted(response_permissions_list), "OK")
        ptprint(" ", "", condition=not self.args.json and bool(response_permissions_list), indent=0)
        self._print_permissions("Missing directives", sorted(missing_permissions), "WARNING")

        if missing_permissions:
            self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-PERMPOLINV")

    def _print_permissions(self, label:str, permissions: list, bullet="OK"):
        if not permissions:
            return
        ptprint(f"{label}:", "", condition=not self.args.json, indent=4)
        for p in permissions:
            if "*" in p:
                bullet="VULN"
                self.ptjsonlib.add_vulnerability("PTV-WEB-HTTP-PERMPOLINV")
            ptprint(p, bullet_type=bullet, condition=not self.args.json, indent=8)

    def _parse_permissions(self, header_value: str):
        return [permission.strip() for permission in header_value.split(",")]