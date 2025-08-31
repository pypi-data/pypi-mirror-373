# Copyright (C) 2021,2022,2023,2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""xsget is a console app that crawl and download online novel.

website: https://github.com/kianmeng/xsget
changelog: https://github.com/kianmeng/xsget/blob/master/CHANGELOG.md
issues: https://github.com/kianmeng/xsget/issues
"""

import argparse
import asyncio
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import parse_qs, unquote, urlparse

import aiohttp
import lxml.html as lxml_html
from bs4 import UnicodeDammit
from playwright.async_api import async_playwright
from user_agent import generate_user_agent

from xsget import (
    EnvironmentAction,
    __version__,
    load_or_create_config,
    setup_logging,
)

CONFIG_FILE = "xsget.toml"

__usages__ = """
examples:
  xsget http://localhost
  xsget http://localhost/page[1-100].html
  xsget -g -l "a" -p "id" http://localhost

"""

_logger = logging.getLogger(__name__)


def url_to_filename(url: str, url_param_as_filename: str = "") -> str:
    """Convert a URL to a filename.

    Args:
        url: The URL to convert
        url_param_as_filename: Extract this URL parameter value as the
        filename.  If empty (default), uses the URL path.

    Returns:
        A filename ending in .html. Returns "index.html" if no suitable name
        found.

    Examples:
        >>> url_to_filename("http://example.com/page1")
        'page1.html'
        >>> url_to_filename("http://example.com/?id=42", "id")
        '42.html'
        >>> url_to_filename("http://example.com/path/to/file.html")
        'file.html'
        >>> url_to_filename("http://example.com/path/to/file?param=value")
        'file.html'

    """
    parsed_url = urlparse(unquote(url))

    if url_param_as_filename:
        query = parse_qs(parsed_url.query)
        if url_param_as_filename in query:
            return query[url_param_as_filename][0] + ".html"

    path = parsed_url.path.rstrip("/")
    filename = Path(path).name
    filename = (
        f"{filename}.html" if not filename.endswith(".html") else filename
    )

    return "index.html" if not filename or filename == ".html" else filename


def extract_urls(decoded_html: str, config: argparse.Namespace) -> List[str]:
    """Extract URLs from HTML based on the CSS Path.

    Args:
        decoded_html (str): The decoded HTML string
        config (argparse.Namespace): Config from command line

    Returns:
        List[str]: A list of URL for downloading
    """
    doc = lxml_html.fromstring(decoded_html)
    doc.make_links_absolute(config.url, resolve_base_href=True)

    return [a.get("href") for a in doc.cssselect(config.link_css_path)]


async def fetch_url_by_aiohttp(
    session: Any, url: str, config: argparse.Namespace
) -> None:
    """Fetch and save a single URL asynchronously.

    Args:
        session (Any): Async session client
        url (str): The URL to download
        config (argparse.Namespace): Config from command line

    Returns:
        None
    """
    try:
        async with session.get(url, timeout=30) as resp:
            resp.raise_for_status()

            content = await resp.text()
            filename_str = url_to_filename(
                str(resp.url), config.url_param_as_filename
            )
            filename = Path(config.output_dir, filename_str)
            filename.parent.mkdir(parents=True, exist_ok=True)

            try:
                with open(filename, "w", encoding=resp.charset) as file:
                    file.write(content)
                    _logger.info("Fetching %s", unquote(str(resp.url)))
                    _logger.info("-> Saving %s", filename)

                return resp
            except IOError as e:
                _logger.error("Error writing to file %s: %s", filename, e)
                return None

    # Log as error instead of raising exception as we want to continue with
    # other downloads.
    except aiohttp.ClientResponseError as error:
        _logger.error("error: %s", error)

    except aiohttp.client_exceptions.InvalidURL as error:
        raise RuntimeError(f"invalid url: {error}") from error


async def fetch_url_by_browser(
    context: Any, url: str, config: argparse.Namespace
) -> None:
    """Fetch and save a single URL asynchronously using Playwright.

    Args:
        context (Any): Playwright browser context.
        url (str): The URL to download.
        config (argparse.Namespace): Config from command line.

    Returns:
        None
    """
    page = None
    try:
        page = await context.new_page()
        await page.wait_for_timeout(config.browser_delay)
        response = await page.goto(url)

        if response is None:
            _logger.error("Failed to get response for URL: %s", url)
            return

        html = await page.content()
        content_type = await response.header_value("content-type")
        encoding = "utf-8"  # Default encoding
        if content_type and ";" in content_type and "=" in content_type:
            try:
                encoding = (
                    content_type.split(";")[1].split("=")[1].strip().lower()
                )
            except IndexError:
                _logger.warning(
                    "Could not parse encoding from content-type: %s",
                    content_type,
                )

        filename_str = url_to_filename(url, config.url_param_as_filename)
        filename = Path(config.output_dir, filename_str)
        filename.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(filename, "w", encoding=encoding) as file:
                file.write(html)
                _logger.info("Fetch: %s -> save: %s", url, filename)
        except IOError as e:
            _logger.error("Error writing to file %s: %s", filename, e)
        except LookupError as e:  # Handle unknown encoding
            _logger.error(
                "Unknown encoding '%s' for file %s: %s", encoding, filename, e
            )
            # Optionally, try writing with a default encoding like utf-8
            try:
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(html)
                _logger.info(
                    "Saved %s with utf-8 encoding after LookupError.", filename
                )
            except Exception as fallback_e:
                _logger.error(
                    "Failed to write %s even with utf-8: %s",
                    filename,
                    fallback_e,
                )

    # Log as error instead of raising exception as we want to continue with
    # other downloads.
    except Exception as error:
        _logger.error("Error fetching URL %s with browser: %s", url, error)
    finally:
        if page:
            await page.close()


async def fetch_urls(
    burls: List[List[str]], config: argparse.Namespace
) -> None:
    """Batch fetch and save multiple URLS asynchronously.

    Args:
        burls (list): A list of URL to be fetched
        config (argparse.Namespace): Config from command line

    Returns:
        None
    """
    if config.browser:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            try:
                for urls in burls:
                    futures = [
                        fetch_url_by_browser(context, url, config)
                        for url in urls
                    ]
                    await asyncio.gather(*futures)
            finally:
                await context.close()
                await browser.close()
    else:
        async with aiohttp.ClientSession(headers=http_headers()) as session:
            for urls in burls:
                futures = [
                    fetch_url_by_aiohttp(session, url, config) for url in urls
                ]
                await asyncio.gather(*futures)


def http_headers() -> Dict[str, str]:
    """Set the user agent for the crawler.

    Returns:
        Dict: Custom HTTP headers, but only User-Agent for now
    """
    return {"User-Agent": generate_user_agent()}


def build_parser(
    args: Optional[Sequence[str]] = None,
) -> argparse.ArgumentParser:
    """Build the CLI parser.

    Args:
        args (list|None): A list of flags from command line.

    Returns:
        argparse.ArgumentParser: Argument parser.
    """
    args = args or []

    parser = argparse.ArgumentParser(
        prog="xsget",
        add_help=False,
        description=__doc__,
        epilog=__usages__,
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(
            prog, max_help_position=8
        ),
    )

    if "-e" not in args or "--env" not in args:
        # should cater for these usages:
        # xsget http://localhost
        # echo "http://localhost" | xsget
        # xsget -c
        # xsget
        nargs = "?" if not sys.stdin.isatty() or "-c" in args else None
        default = sys.stdin.read().rstrip() if not sys.stdin.isatty() else ""
        parser.add_argument(
            dest="url",
            help="set url of the index page to crawl",
            type=str,
            metavar="URL",
            nargs=nargs,  # type: ignore
            default=default,
        )

    parser.add_argument(
        "-l",
        "--link-css-path",
        default="a",
        dest="link_css_path",
        help="set css path of the link to a chapter (default: '%(default)s')",
        type=str,
        metavar="CSS_PATH",
    )

    parser.add_argument(
        "-p",
        "-url-param-as-filename",
        default="",
        dest="url_param_as_filename",
        help="use url param key as filename (default: '')",
        type=str,
        metavar="URL_PARAM",
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-g",
        "--generate-config-file",
        nargs="?",
        default=False,
        const=CONFIG_FILE,
        dest="generate_config",
        help="generate config file from options (default: '%(const)s')",
        type=str,
        metavar="FILENAME",
    )

    group.add_argument(
        "-c",
        "--config-file",
        nargs="?",
        default=False,
        const=CONFIG_FILE,
        dest="config",
        help="load config from file (default: '%(const)s')",
        type=str,
        metavar="FILENAME",
    )

    parser.add_argument(
        "-r",
        "--refresh",
        action="store_true",
        dest="refresh",
        help="refresh the index page",
    )

    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        dest="test",
        help="show extracted urls without crawling",
    )

    parser.add_argument(
        "-b",
        "--browser",
        default=False,
        action="store_true",
        dest="browser",
        help="crawl by actual browser (default: '%(default)s')",
    )

    parser.add_argument(
        "-bs",
        "--browser-session",
        default=2,
        dest="browser_session",
        help="set the number of browser session (default: %(default)s)",
        type=int,
        metavar="SESSION",
    )

    parser.add_argument(
        "-bd",
        "--browser-delay",
        default=0,
        dest="browser_delay",
        help=(
            "set the second to wait for page to load in browser "
            "(default: %(default)s)"
        ),
        type=int,
        metavar="DELAY",
    )

    parser.add_argument(
        "-od",
        "--output-dir",
        dest="output_dir",
        default="output",
        help="set default output folder (default: '%(default)s')",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        default=False,
        action="store_true",
        dest="quiet",
        help="suppress all logging",
    )

    parser.add_argument(
        "-e",
        "--env",
        default=False,
        action=EnvironmentAction,
        dest="env",
        help="print environment information for bug reporting",
    )

    parser.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        dest="debug",
        help="show debugging log and stacktrace",
    )

    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="show this help message and exit",
    )

    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    return parser


def filter_urls(index_html: Path, config: argparse.Namespace) -> List[Any]:
    """Extract and filter list of URLs for crawling.

    Args:
        index_html (Path): Main index HTML file.
        config (argparse.Namespace): Config from command line.

    Return:
        List[Any]: List or batches of list of URLs.
    """
    eurls = []
    with open(index_html, "rb") as file:
        dammit = UnicodeDammit(file.read())
        decoded_html = dammit.unicode_markup
        eurls = extract_urls(decoded_html, config)
        _logger.info("Total URL extracted: %d", len(eurls))

    for url in eurls.copy():
        filename_str = url_to_filename(url, config.url_param_as_filename)
        filename = Path(config.output_dir, filename_str)
        if filename.exists():
            eurls.remove(url)
            _logger.info("Found file %s", filename)
            _logger.info("Skip downloading %s", unquote(str(url)))

    burls = []
    if config.browser and config.browser_session:
        batch = config.browser_session
        burls = [eurls[i : i + batch] for i in range(0, len(eurls), batch)]
    else:
        burls = [eurls]

    _logger.info("Total URL to download: %d", len(eurls))
    _logger.info("Total URL batches to download: %d", len(burls))
    return burls


async def _main_async_logic(config: argparse.Namespace) -> None:
    """Encapsulates the main asynchronous logic for fetching URLs."""
    range_re = r"\[(.*)\-(.*)\]"
    match = re.search(range_re, config.url)

    if match:
        urls_in_range = []
        start = int(match.group(1))
        end = int(match.group(2))

        if start > end:
            raise RuntimeError(f"invalid url range, start: {start}, end: {end}")

        for sequence in range(start, end + 1):
            url = config.url.replace(match.group(0), str(sequence), 1)
            urls_in_range.append(url)

        burls = [urls_in_range]
    else:
        filename_str = url_to_filename(
            config.url, config.url_param_as_filename
        )
        filename = Path(config.output_dir, filename_str)

        if config.refresh:
            _logger.info("Refresh the index url: %s", config.url)
            if filename.exists():
                filename.unlink()

        await fetch_urls([[config.url]], config)

        burls = filter_urls(filename, config)

    if config.test:
        for urls_batch in burls:
            for url in urls_batch:
                _logger.info("Found url: %s", url)
    else:
        await fetch_urls(burls, config)


def run(config: argparse.Namespace) -> None:
    """Run the asyncio main flow.

    Args:
        config (argparse.Namespace): Config from command line arguments or
        config file.
    """
    asyncio.run(_main_async_logic(config), debug=config.debug)


def main(args: Optional[Sequence[str]] = None) -> None:
    """Run the main program flow."""
    args = args or sys.argv[1:]
    _logger.debug(args)

    try:
        parser = build_parser(args)
        parsed_args = parser.parse_args(args)

        setup_logging(parsed_args)

        _logger.debug(args)
        _logger.debug(parsed_args)

        config_from_file = load_or_create_config(parsed_args, "xsget")
        parser.set_defaults(**config_from_file)
        config = parser.parse_args()

        run(config)
    except Exception as error:
        _logger.error(
            "error: %s",
            getattr(error, "message", str(error)),
            exc_info=("-d" in args or "--debug" in args),
        )
        raise SystemExit(1) from None


def cli():
    """Set the main entrypoint of the console app."""
    main(sys.argv[1:])


if __name__ == "__main__":
    cli()
    raise SystemExit()
