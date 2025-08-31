# xsget

Console tools to download online novel and convert to text file.

## Installation

Stable version From PyPI using `uv`:

```console
uv tool install xsget playwright
playwright install
```

Upgrade to latest stable version:

```console
uv tool upgrade xsget
```

Latest development version from GitHub:

```console
python3 -m pip install -e git+https://github.com/kianmeng/xsget.git
playwright install
```

## xsget

```console
xsget -h
```

<!--help-xsget !-->

```console
usage: xsget [-l CSS_PATH] [-p URL_PARAM] [-g [FILENAME] | -c [FILENAME]] [-r]
             [-t] [-b] [-bs SESSION] [-bd DELAY] [-od OUTPUT_DIR] [-q] [-e]
             [-d] [-h] [-V]
             URL

xsget is a console app that crawl and download online novel.

website: https://github.com/kianmeng/xsget
changelog: https://github.com/kianmeng/xsget/blob/master/CHANGELOG.md
issues: https://github.com/kianmeng/xsget/issues

positional arguments:
  URL   set url of the index page to crawl

options:
  -l, --link-css-path CSS_PATH
        set css path of the link to a chapter (default: 'a')
  -p, -url-param-as-filename URL_PARAM
        use url param key as filename (default: '')
  -g, --generate-config-file [FILENAME]
        generate config file from options (default: 'xsget.toml')
  -c, --config-file [FILENAME]
        load config from file (default: 'xsget.toml')
  -r, --refresh
        refresh the index page
  -t, --test
        show extracted urls without crawling
  -b, --browser
        crawl by actual browser (default: 'False')
  -bs, --browser-session SESSION
        set the number of browser session (default: 2)
  -bd, --browser-delay DELAY
        set the second to wait for page to load in browser (default: 0)
  -od, --output-dir OUTPUT_DIR
        set default output folder (default: 'output')
  -q, --quiet
        suppress all logging
  -e, --env
        print environment information for bug reporting
  -d, --debug
        show debugging log and stacktrace
  -h, --help
        show this help message and exit
  -V, --version
        show program's version number and exit

examples:
  xsget http://localhost
  xsget http://localhost/page[1-100].html
  xsget -g -l "a" -p "id" http://localhost
```

<!--help-xsget !-->

## xstxt

```console
xstxt -h
```

<!--help-xstxt !-->

```console
usage: xstxt [-pt CSS_PATH] [-pb CSS_PATH] [-la LANGUAGE] [-ps SEPARATOR]
             [-rh REGEX REGEX] [-rt REGEX REGEX] [-bt TITLE] [-ba AUTHOR]
             [-ic INDENT_CHARS] [-fw] [-oi] [-ow] [-i GLOB_PATTERN]
             [-e GLOB_PATTERN] [-l TOTAL_FILES] [-w WIDTH] [-o FILENAME]
             [-od OUTPUT_DIR] [-y] [-p] [-g [FILENAME] | -c [FILENAME]] [-m]
             [-q] [--env] [-d] [-h] [-V]

xstxt is a console app that extract content from HTML to text file.

website: https://github.com/kianmeng/xsget
changelog: https://github.com/kianmeng/xsget/blob/master/CHANGELOG.md
issues: https://github.com/kianmeng/xsget/issues

options:
  -pt, --title-css-path CSS_PATH
        set css path of chapter title (default: 'title')
  -pb, --body-css-path CSS_PATH
        set css path of chapter body (default: 'body')
  -la, --language LANGUAGE
        language of the ebook (default: 'zh')
  -ps, --paragraph-separator SEPARATOR
        set paragraph separator (default: '\n\n')
  -rh, --html-replace REGEX REGEX
        set regex to replace word or pharase in html file
  -rt, --txt-replace REGEX REGEX
        set regex to replace word or pharase in txt file
  -bt, --book-title TITLE
        set title of the novel (default: '不详')
  -ba, --book-author AUTHOR
        set author of the novel (default: '不详')
  -ic, --indent-chars INDENT_CHARS
        set indent characters for a paragraph (default: '')
  -fw, --fullwidth
        convert ASCII character to from halfwidth to fullwidth (default: 'False')
  -oi, --output-individual-file
        convert each html file into own txt file
  -ow, --overwrite
        overwrite output file
  -i, --input GLOB_PATTERN
        set glob pattern of html files to process (default: '['./*.html']')
  -e, --exclude GLOB_PATTERN
        set glob pattern of html files to exclude (default: '[]')
  -l, --limit TOTAL_FILES
        set number of html files to process (default: '3')
  -w, --width WIDTH
        set the line width for wrapping (default: 0, 0 to disable)
  -o, --output FILENAME
        set output txt file name (default: 'book.txt')
  -od, --output-dir OUTPUT_DIR
        set output directory (default: 'output')
  -y, --yes
        yes to prompt
  -p, --purge
        remove extracted files specified by --output-folder option (default: 'False')
  -g, --generate-config-file [FILENAME]
        generate config file from options (default: 'xstxt.toml')
  -c, --config-file [FILENAME]
        load config from file (default: 'xstxt.toml')
  -m, --monitor
        monitor config file changes and re-run when needed
  -q, --quiet
        suppress all logging
  --env
        print environment information for bug reporting
  -d, --debug
        show debugging log and stacktrace
  -h, --help
        show this help message and exit
  -V, --version
        show program's version number and exit

examples:
  xsget -g
  xstxt --input *.html
  xstxt --output-individual-file --input *.html
  xstxt --config --monitor
```

<!--help-xstxt !-->

## Copyright and License

Copyright (C) 2021,2022,2023,2024,2025 Kian-Meng Ang

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along
with this program. If not, see <https://www.gnu.org/licenses/>.
