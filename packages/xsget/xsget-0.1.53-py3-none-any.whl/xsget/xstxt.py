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

"""xstxt is a console app that extract content from HTML to text file.

website: https://github.com/kianmeng/xsget
changelog: https://github.com/kianmeng/xsget/blob/master/CHANGELOG.md
issues: https://github.com/kianmeng/xsget/issues
"""

import argparse
import asyncio
import gettext
import glob
import logging
import math
import os
import shutil
import sys
import textwrap
from pathlib import Path
from typing import Callable, List, Optional, Sequence

import aiofiles
import regex as re
from bs4 import BeautifulSoup, UnicodeDammit
from natsort import natsorted
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from xsget import (
    EnvironmentAction,
    __version__,
    load_or_create_config,
    setup_logging,
)
from xsget.chapter import Chapter

__usages__ = """
examples:
  xsget -g
  xstxt --input *.html
  xstxt --output-individual-file --input *.html
  xstxt --config --monitor

"""

# Unicode integer in hexadecimal for these characters.
FULLWIDTH_EXCLAMATION_MARK = 0xFF01
EXCLAMATION_MARK = 0x21
TILDE = 0x7E

# Fullwidth is a text character that occupies two alphanumeric characters
# in monospace font.
#
# See Halfwidth and Fullwidth Forms in Unicode (https://w.wiki/66Ps) and
# Unicode block (https://w.wiki/66Pt).
HALFWIDTH_FULLWIDTH_MAP = {}
for halfwidth_i, fullwidth_i in enumerate(range(EXCLAMATION_MARK, TILDE + 1)):
    HALFWIDTH_FULLWIDTH_MAP[fullwidth_i] = (
        FULLWIDTH_EXCLAMATION_MARK + halfwidth_i
    )

DEFAULT_CONFIG_FILE = "xstxt.toml"

_logger = logging.getLogger(__name__)


class ConfigFileHandler(FileSystemEventHandler):
    """Custom event handler for monitoring changes in config file."""

    def __init__(self, config) -> None:
        """Initialize the config file handler.

        Args:
            config: Configuration from `xstxt.toml`

        """
        self.config = config

    def on_modified(self, event) -> None:
        """Re-generate the book when config file updated."""
        if event.src_path.endswith(DEFAULT_CONFIG_FILE):
            config = _load_config(["-c", self.config.config])
            asyncio.run(generate_book(config), debug=config.debug)


def get_html_files(
    inputs: List[str], limit: int, excludes: List[str]
) -> List[str]:
    """Get the list of HTML files or file for cleansing and extracting.

    Args:
        inputs (List[str]): Glob-like pattern for selecting HTML files
        limit (int): Number of HTML files to process
        excludes (List[str]): Glob-like pattern for excluding HTML files

    Returns:
        List[str]: Number of HTML file names
    """
    input_files: List[str] = []
    for pattern in inputs:
        _logger.debug("HTML source input: %s", pattern)
        found_files = glob.glob(pattern, recursive=True)
        if not found_files:
            _logger.error("No input files found in: %s", pattern)

        input_files.extend(found_files)

    exclude_files: List[str] = []
    for pattern in excludes:
        _logger.debug("HTML source exclude: %s", pattern)
        found_files = glob.glob(pattern, recursive=True)
        if not found_files:
            _logger.error("No exclude files found in: %s", pattern)

        exclude_files.extend(found_files)

    files = natsorted(list(set(input_files) - set(exclude_files)), key=str)
    return files[:limit] if limit > 0 else files


async def generate_book(config: argparse.Namespace) -> None:
    """Extract all chapters from HTML files into single text file.

    Args:
        config (argparse.Namespace): config from args or file
    """
    html_files = get_html_files(config.input, config.limit, config.exclude)
    total_files = len(html_files)
    _logger.info("Processing total files: %d", total_files)

    futures = []
    for i, filename in enumerate(html_files, start=1):
        if config.debug:
            _logger.debug("Processing file: %s", filename)
        else:
            percent = round(i / total_files * 100, 1)
            progress = f"({percent}% - {i} / {total_files})"
            print(
                f"Processing file: {filename} {progress}", end="\r", flush=True
            )

        async with aiofiles.open(filename, "rb") as file:
            dammit = UnicodeDammit(await file.read())
            decoded_html = dammit.unicode_markup
            futures.append(extract_chapter(decoded_html, config, filename))

    chapters = await asyncio.gather(*futures)
    # Clear the progress line only if running in a TTY
    if sys.stdout.isatty():
        print(" " * os.get_terminal_size()[0], end="\r")

    cwd = Path(os.getcwd(), config.output_dir, config.output).parent
    if config.purge and cwd.exists() and not config.yes:
        _logger.debug("Purge output folder: %s", cwd)
        shutil.rmtree(cwd)

    if config.output_individual_file:
        generate_multiple_txt(chapters, config)
    else:
        generate_single_txt(chapters, config)


async def extract_chapter(
    decoded_html: BeautifulSoup,
    config: argparse.Namespace,
    filename: str = "",
) -> Chapter:
    """Extract chapter from the decoded HTML.

    Args:
        decoded_html (BeautifulSoup): decoded HTML text
        config (argparse.Namespace): config from args or file
        filename (str): the filename of the decoded html

    Returns:
        Chapter: extracted chapters
    """
    html = decoded_html
    if config.html_replace:
        html = search_and_replace(decoded_html, config.html_replace)

    soup = BeautifulSoup(html, features="lxml")
    title = extract_title(soup, config.title_css_path)
    body = extract_body(soup, config.body_css_path)

    chapter = Chapter(title, body.rstrip(), filename)

    if config.debug:
        _logger.debug("Processing %s", repr(chapter))
    else:
        print(f"Processing {repr(chapter)}", end="\r")

    return chapter


def extract_title(decoded_html: BeautifulSoup, css_path: Optional[str]) -> str:
    """Extract title of a chapter from HTML.

    Args:
        decoded_html (BeautifulSoup): HTML text
        css_path (str): CSS path to a title of a chapter

    Returns:
        str: title of a chapter
    """
    if not css_path:
        return ""

    title = decoded_html.select_one(css_path)
    return title.text.strip() if title else ""


def extract_body(html: BeautifulSoup, css_path: str) -> str:
    """Extract body of a chapter from HTML.

    Args:
        html (BeautifulSoup): HTML text
        css_path (str): CSS path to a body of a chapter

    Returns:
        str: The body of HTML page if found, otherwise empty string.
    """
    if not css_path:
        return ""

    body = html.select_one(css_path)
    return body.text if body else ""


def search_and_replace(content: str, regexs: list) -> str:
    """Replace words/phrases based on a list of regex.

    Args:
        content (str): HTML or plain text
        regexs (list): List of regex rules

    Returns:
        str: HTML or plain text
    """
    try:
        compiled_regexs = []
        for search, replace in regexs:
            _logger.debug(
                "search: %s -> replace: %s", repr(search), repr(replace)
            )
            compiled_regexs.append(
                (re.compile(rf"{search}", re.MULTILINE), rf"{replace}")
            )  # pylint: disable=no-member

        for before, after in compiled_regexs:
            content = re.sub(before, after, content)
    except re.error as error:  # Catch regex compilation errors
        _logger.error("Invalid regex: %s", error)
        return content  # Return original content on error
    except (
        ValueError
    ) as error:  # Catch unpacking errors for malformed regexs list
        _logger.error("Invalid regex: %s", error)
        return content

    return content


def wrap(content: str, config: argparse.Namespace) -> str:
    """Wrap the content to a length.

    We assume that each paragraph was separated by an empty line.

    config.width is the length of the line to wrap.

    If the content falls within Unicode CJK Unified Ideographs code block
    (4E00—9FFF), we treat it as multi-bytes character and divide the configured
    width by 2.

    And text wrapping for CJK text is rather complicated. See
    https://github.com/python/cpython/issues/68853.

    Args:
        content (str): HTML or plain text.
        config (argparse.Namespace): config from args or file

    Returns:
        str: HTML or plain text
    """
    if not content:
        return content

    options = {}

    if config.width > 0:
        calculated_width = config.width
        if re.search(r"[\u4e00-\u9fff]+", content):
            calculated_width = math.floor(config.width // 2)

        _logger.debug(
            "Wrap paragraph at width: calculated: %d, configured: %d",
            calculated_width,
            config.width,
        )
        options["width"] = calculated_width

    paragraphs = []
    # Assuming each paragraph was separated by an empty line based on default
    # value for `-ps` argument.
    for paragraph in content.split(config.paragraph_separator):
        if config.indent_chars != "":
            paragraph = textwrap.dedent(paragraph).strip()
            options["initial_indent"] = config.indent_chars
            # default `width` is 70 if not set and we need to set to larger
            # value instead.
            if config.width < 0:
                options["width"] = sys.maxsize

        if config.width > 0:
            paragraph = paragraph.rstrip().replace("\n", "")

        if options:
            _logger.debug(options)
            paragraph = textwrap.fill(paragraph, **options)

        paragraphs.append(paragraph)

    wrapped_content = config.paragraph_separator.join(paragraphs)
    return wrapped_content


def generate_multiple_txt(
    chapters: list[Chapter], config: argparse.Namespace
) -> None:
    """Write the extracted book into multiple txt file.

    Args:
        chapters (list): A list of Chapter.
        config (argparse.Namespace): config from args or file
    """
    for chapter in chapters:
        content = str(chapter)
        if config.txt_replace:
            content = search_and_replace(content, config.txt_replace)

        if config.fullwidth:
            _logger.info("Converting halfwidth ASCII to fullwidth")
            content = content.translate(HALFWIDTH_FULLWIDTH_MAP)

        content = wrap(content, config)

        filename = Path(
            config.output_dir, Path(chapter.filename).stem + ".txt"
        )
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", newline="\n", encoding="utf8") as file:
            file.write(content)


def generate_single_txt(
    chapters: list[Chapter], config: argparse.Namespace
) -> None:
    """Write the extracted book into single txt file.

    Args:
        chapters (list): A list of Chapters
        config (argparse.Namespace): config from args or file
    """
    filename = Path(config.output_dir, config.output)
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", newline="\n", encoding="utf8") as file:
        _ = _load_translation(config)
        file.write("---\n")
        file.write(_("title:") + config.book_title + "\n")
        file.write(_("author:") + config.book_author + "\n")
        file.write(f"---{config.paragraph_separator}")

        chapter_strings = [str(chapter) for chapter in chapters]
        content = config.paragraph_separator.join(chapter_strings)

        if config.txt_replace:
            content = search_and_replace(content, config.txt_replace)

        if config.fullwidth:
            _logger.info("Converting halfwidth ASCII to fullwidth")
            content = content.translate(HALFWIDTH_FULLWIDTH_MAP)

        content = wrap(content, config)

        file.write(content)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        prog="xstxt",
        add_help=False,
        description=__doc__,
        epilog=__usages__,
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(
            prog, max_help_position=8
        ),
    )
    parser.add_argument(
        "-pt",
        "--title-css-path",
        default="title",
        dest="title_css_path",
        help="set css path of chapter title (default: '%(default)s')",
        type=str,
        metavar="CSS_PATH",
    )
    parser.add_argument(
        "-pb",
        "--body-css-path",
        default="body",
        dest="body_css_path",
        help="set css path of chapter body (default: '%(default)s')",
        type=str,
        metavar="CSS_PATH",
    )
    parser.add_argument(
        "-la",
        "--language",
        dest="language",
        default="zh",
        help="language of the ebook (default: '%(default)s')",
        metavar="LANGUAGE",
    )
    parser.add_argument(
        "-ps",
        "--paragraph-separator",
        dest="paragraph_separator",
        type=lambda value: value.encode("utf-8").decode("unicode_escape"),
        default="\n\n",
        help="set paragraph separator (default: %(default)r)",
        metavar="SEPARATOR",
    )
    parser.add_argument(
        "-rh",
        "--html-replace",
        default=[],
        action="append",
        dest="html_replace",
        nargs=2,
        help="set regex to replace word or pharase in html file",
        type=str,
        metavar="REGEX",
    )
    parser.add_argument(
        "-rt",
        "--txt-replace",
        default=[],
        action="append",
        dest="txt_replace",
        nargs=2,
        help="set regex to replace word or pharase in txt file",
        type=str,
        metavar="REGEX",
    )
    parser.add_argument(
        "-bt",
        "--book-title",
        default="不详",
        dest="book_title",
        help="set title of the novel (default: '%(default)s')",
        type=str,
        metavar="TITLE",
    )
    parser.add_argument(
        "-ba",
        "--book-author",
        default="不详",
        dest="book_author",
        help="set author of the novel (default: '%(default)s')",
        type=str,
        metavar="AUTHOR",
    )
    parser.add_argument(
        "-ic",
        "--indent-chars",
        default="",
        dest="indent_chars",
        help=(
            "set indent characters for a paragraph (default: '%(default)s')"
        ),
        type=str,
        metavar="INDENT_CHARS",
    )
    parser.add_argument(
        "-fw",
        "--fullwidth",
        default=False,
        action="store_true",
        dest="fullwidth",
        help=(
            "convert ASCII character to from halfwidth to fullwidth "
            "(default: '%(default)s')"
        ),
    )
    parser.add_argument(
        "-oi",
        "--output-individual-file",
        default=False,
        action="store_true",
        dest="output_individual_file",
        help="convert each html file into own txt file",
    )
    parser.add_argument(
        "-ow",
        "--overwrite",
        default=False,
        action="store_true",
        dest="overwrite",
        help="overwrite output file",
    )

    parser.add_argument(
        "-i",
        "--input",
        default=["./*.html"],
        action="append",
        dest="input",
        help=(
            "set glob pattern of html files to process "
            "(default: '%(default)s')"
        ),
        type=str,
        metavar="GLOB_PATTERN",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        default=[],
        action="append",
        dest="exclude",
        help=(
            "set glob pattern of html files to exclude "
            "(default: '%(default)s')"
        ),
        type=str,
        metavar="GLOB_PATTERN",
    )
    parser.add_argument(
        "-l",
        "--limit",
        default=3,
        dest="limit",
        help="set number of html files to process (default: '%(default)s')",
        type=int,
        metavar="TOTAL_FILES",
    )
    parser.add_argument(
        "-w",
        "--width",
        default=0,
        dest="width",
        help="set the line width for wrapping "
        "(default: %(default)s, 0 to disable)",
        type=int,
        metavar="WIDTH",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="book.txt",
        dest="output",
        help="set output txt file name (default: '%(default)s')",
        type=str,
        metavar="FILENAME",
    )
    parser.add_argument(
        "-od",
        "--output-dir",
        default="output",
        dest="output_dir",
        help="set output directory (default: '%(default)s')",
        type=str,
        metavar="OUTPUT_DIR",
    )

    parser.add_argument(
        "-y",
        "--yes",
        default=False,
        action="store_true",
        dest="yes",
        help="yes to prompt",
    )

    parser.add_argument(
        "-p",
        "--purge",
        default=False,
        action="store_true",
        dest="purge",
        help=(
            "remove extracted files specified by --output-folder option "
            "(default: '%(default)s')"
        ),
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-g",
        "--generate-config-file",
        nargs="?",
        default=False,
        const=DEFAULT_CONFIG_FILE,
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
        const=DEFAULT_CONFIG_FILE,
        dest="config",
        help="load config from file (default: '%(const)s')",
        type=str,
        metavar="FILENAME",
    )

    parser.add_argument(
        "-m",
        "--monitor",
        default=False,
        action="store_true",
        dest="monitor",
        help="monitor config file changes and re-run when needed",
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


def main(args: Optional[Sequence[str]] = None) -> None:
    """Run the main program flow."""
    args = args or sys.argv[1:]
    _logger.debug(args)

    try:
        config = _load_config(args)
        _logger.debug(config)

        asyncio.run(generate_book(config), debug=config.debug)
        if config.monitor:
            _run_monitor(config)
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


def _run_monitor(config: argparse.Namespace) -> None:
    """Monitor the config file changes in the background.

    Args:
        config(dict): Config from file.
    """
    observer = Observer()
    try:
        _logger.info("Running in monitor mode")
        event_handler = ConfigFileHandler(config)
        observer.schedule(event_handler, path=".")
        observer.start()

        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()


def _load_config(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Load configuration from file and command line arguments."""
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    setup_logging(parsed_args)

    config_from_file = load_or_create_config(parsed_args, "xstxt")
    parser.set_defaults(**config_from_file)
    config = parser.parse_args()
    return config


def _load_translation(config: argparse.Namespace) -> Callable:
    """Load translation for the given language."""
    localedir = Path(Path(__file__).parent, "locales")
    _logger.debug("locale directory: %s", localedir)

    translation = gettext.translation(
        "xstxt", localedir=localedir, languages=[config.language]
    )
    return translation.gettext


if __name__ == "__main__":
    cli()
    raise SystemExit()
