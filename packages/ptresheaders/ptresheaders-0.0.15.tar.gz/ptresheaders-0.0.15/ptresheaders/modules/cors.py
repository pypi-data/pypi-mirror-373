#from modules.headers._header_test_base import HeaderTestBase
from ptlibs.ptprinthelper import ptprint

class CrossOriginResourceSharing:

    def test(self, args, response_headers: dict):

        """
        _cors_headers = [h.lower() for h in [
            "Cross-Origin-Resource-Policy", "Cross-Origin-Opener-Policy", "Cross-Origin-Embedder-Policy",
            "Access-Control-Max-Age", "Access-Control-Expose-Headers", "Access-Control-Allow-Credentials",
            "Access-Control-Allow-Headers", "Access-Control-Allow-Methods", "Access-Control-Allow-Origin"
        ]]
        """

        cross_origin_headers = self.get_cors_headers(response_headers)

        if cross_origin_headers:
            ptprint("CORS Header:", bullet_type="TITLE", condition=not args.json, colortext=True, newline_above=True)

            for header_dict in cross_origin_headers:
                header_name, value = next(iter(header_dict.items()))  # Unpack the single key-value pair
                bullet, output_value = self._analyze_header(header_name, value)
                # Print each CORS header with details
                ptprint(f'{header_name}: {output_value}', bullet_type=bullet, condition=not args.json, indent=4)

    def _analyze_header(self, header_name: str, value: str):
        """Analyze the CORS header to determine if there are vulnerabilities or additional notes."""
        bullet = ""
        output_value = value

        if header_name.lower() == "access-control-allow-origin":
            for origin in value.split():
                if origin == "*":
                    bullet = "VULN"
                    break
                elif origin == "https://www.example.com/":
                    bullet = "VULN"
                    output_value += " (reflective origin)"
                    break

        return bullet, output_value

    def get_cors_headers(self, headers: dict):
        """
        Extract CORS-related headers from the provided response headers.

        :param headers: dict
            The HTTP response headers to filter.
        :return: list
            A list of CORS-related headers as key-value dictionaries.
        """
        cors_headers: list = [
            {key: value} for key, value in headers.items()
            if key.lower().startswith("access-control") or key.lower().startswith("cross-origin")
        ]
        return cors_headers