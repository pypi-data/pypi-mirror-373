[![penterepTools](https://www.penterep.com/external/penterepToolsLogo.png)](https://www.penterep.com/)


## PTMULTIFINDER - Custom Source Domain Testing Tool

ptmultifinder automates the testing of multiple domains from a provided wordlist. It connects to each domain and checks against specified sources to identify matches. It also verifies the existence of the specified sources. Ideal for bulk domain analysis and discovering specific types of domains.

## Installation
```
pip install ptmultifinder
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
ptmultifinder --domains domains.txt --sources sources.txt
ptmultifinder --domains domains.txt --sources admin.php .git/ backup/
```

## Options
```
-d   --domains         <domains>       Domains or file with domains to test
-s   --source          <source>        Sources or file with sources to check
-sc  --status-code     <status-code>   Specify status codes that will be accepted (default 200)
-sy  --string-yes      <string>        Show only results that contain the specified string in the response
-sn  --string-no       <string>        Show only results that do not contain the specific string in the response
-cs  --case-sensitive                  Enable case sensitivity for -sy, -sn options
-ch  --check                           Skip domain if it responds with a status code of 200 to a non-existent resource.
-p   --proxy           <proxy>         Set Proxy
-a   --user-agent      <agent>         Set User-Agent
-t   --threads         <threads>       Set Threads count
-T   --timeout         <timeout>       Set Timeout (default 5s)
-H   --headers         <header:value>  Set custom headers
-v   --version                         Show script version and exit
-h   --help                            Show this help message and exit
-j   --json                            Output in JSON format
```

## Dependencies
```
ptlibs
bs4
lxml
```

## License

Copyright (c) 2025 Penterep Security s.r.o.

ptmultifinder is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

ptmultifinder is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with ptmultifinder. If not, see https://www.gnu.org/licenses/.

## Warning

You are only allowed to run the tool against the websites which
you have been given permission to pentest. We do not accept any
responsibility for any damage/harm that this application causes to your
computer, or your network. Penterep is not responsible for any illegal
or malicious use of this code. Be Ethical!