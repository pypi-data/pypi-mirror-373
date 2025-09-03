[![penterepTools](https://www.penterep.com/external/penterepToolsLogo.png)](https://www.penterep.com/)


## PTRESHEADERS - Response Headers Testing Tool

ptresheaders is an automated tool that efficiently analyzes and tests HTTP response headers for security best practices and compliance with industry standards.

## Installation

```
pip install ptresheaders
```

## Adding to PATH
If you're unable to invoke the script from your terminal, it's likely because it's not included in your PATH. You can resolve this issue by executing the following commands, depending on the shell you're using:

For Bash Users
```bash
echo "export PATH=\"`python3 -m site --user-base`/bin:\$PATH\"" >> ~/.bashrc
source ~/.bashrc
```

For ZSH Users
```bash
echo "export PATH=\"`python3 -m site --user-base`/bin:\$PATH\"" >> ~/.zshrc
source ~/.zshrc
```

## Usage examples
```
ptresheaders -u https://www.example.com
ptresheaders -u https://www.example.com --proxy 127.0.0.1:8080
```

## Options
```
-u   --url           <url>           Connect to URL
-p   --proxy         <proxy>         Set proxy
-c   --cookie        <cookie>        Set cookie
-H   --headers       <header:value>  Set headers
-a   --user-agent    <agent>         Set User-Agent
-T   --timeout                       Set timeout
-m   --method                        Set method (default GET)
-r   --redirects                     Follow redirects
-C   --cache                         Enable HTTP cache
-j   --json                          Enable JSON output
-v   --version                       Show script version and exit
-h   --help                          Show this help message and exit
```

## Dependencies
```
ptlibs
ptcookiechecker
bs4
lxml
```

## License

Copyright (c) 2024 Penterep Security s.r.o.

ptresheaders is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

ptresheaders is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with ptresheaders. If not, see https://www.gnu.org/licenses/.

## Warning

You are only allowed to run the tool against the websites which
you have been given permission to pentest. We do not accept any
responsibility for any damage/harm that this application causes to your
computer, or your network. Penterep is not responsible for any illegal
or malicious use of this code. Be Ethical!