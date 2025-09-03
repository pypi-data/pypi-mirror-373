from ptlibs import ptmisclib
from ptlibs.ptprinthelper import ptprint, out_if

import os, re

LEAKING_HEADERS = [
    "server",
    "x-powered-by",
    "x-aspnet-version",
    "x-aspnetmvc-version",
    "accept-language",
    "x-real-ip",
    "x-forwarded-for",
    "x-forwarded-proto",
    "x-cluster-client-ip",
    "x-content-digest",
    "x-request-id",
    "x-ua-compatible",
    "x-b3-traceid",
    "x-b3-spanid",
    "x-b3-parentspanid",
    "x-tyk-authorization",
    "x-amz-id-2",
    "x-amz-request-id",
    "via",
    "etag",
    "x-cloud-trace-context",
    "x-microsoft-diagnostics-applicationanalytics",
    "x-microsoft-diagnostics-serviceversion",
    "x-microsoft-request-id"
    "cache-control",
]

class LeaksFinder():
    def __init__(self, args, ptjsonlib):
        self.ptjsonlib = ptjsonlib
        self.args = args

    def find_technology_headers(self, headers: dict):
        leaking_headers = [
            out_if(string=f"{header_name}: {header_value}\n", bullet_type="TEXT", condition=not self.args.json, indent=4)
            for header_name, header_value in headers.items()
            if header_name.lower() in LEAKING_HEADERS
        ]

        output = "".join(leaking_headers).rstrip("\n")
        ptprint(f"Info leaking headers:", "INFO", not self.args.json and output, newline_above=True, colortext=True)
        ptprint(output, "TEXT", True, indent=0, end="\n")

    def find_leaking_domains(self, headers: dict):
        tlds = ptmisclib.get_tlds()
        domain_pattern = r"(?:\*\.|[a-zA-Z0-9-]+\.)*[a-zA-Z0-9-]+\.(?:[a-zA-Z]{2,})(?::\d{1,5})?(?=\b)"

        potential_domains = re.findall(domain_pattern, str(headers))
        valid_domains = sorted(set([domain for domain in potential_domains if domain.split('.')[-1].split(":")[0].upper() in tlds])) # if 'tld' ends with tld
        ptprint(f"Domains in headers:", "INFO", not self.args.json and valid_domains, newline_above=True, colortext=True)
        for d in valid_domains:
            if d.lower() not in ["asp.net"]:
                ptprint(d, "TEXT", not self.args.json, indent=4, end="\n")


    def find_ipv4(self, headers: dict):
        """Find IPv4 addresses in provided string"""
        ipv4_pattern = r'((?<![\d.])(?:(?:[1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(?:[1-9]?\d|1\d\d|2[0-4]\d|25[0-5]))(:\d{1,4})?(?![\d.])'
        valid_ips = sorted(set(re.findall(ipv4_pattern, str(headers))))
        ptprint(f"IPv4 in headers:", "INFO", not self.args.json and valid_ips, newline_above=True, colortext=True)
        for ip in valid_ips:
            ptprint(''.join(ip), "TEXT", not self.args.json, indent=4, end="\n")
