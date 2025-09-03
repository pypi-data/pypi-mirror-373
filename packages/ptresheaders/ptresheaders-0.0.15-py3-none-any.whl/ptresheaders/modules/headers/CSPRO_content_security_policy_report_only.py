from modules.headers.CSP_content_security_policy import ContentSecurityPolicy

class ContentTypeReportOnly(ContentSecurityPolicy):
    def test_header(self, header_value):
        super().test_header(header_value)