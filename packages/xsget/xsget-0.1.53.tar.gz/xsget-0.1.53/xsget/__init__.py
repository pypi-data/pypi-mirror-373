# Copyright (C) 2021,2022,2023,2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Console tools to download online novel and convert to text file."""

import argparse
import logging
import os
import platform
import sys
from datetime import datetime as dt
from importlib.resources import read_text
from pathlib import Path
from typing import Any, Dict

import tomlkit

__version__ = "0.1.53"

_logger = logging.getLogger(__name__)


class ConfigFileCorruptedError(Exception):
    """Config file corrupted after reading."""


class ConfigFileExistsError(Exception):
    """Config file found when generating a new config file."""


def setup_logging(parsed_args: argparse.Namespace) -> None:
    """Set up logging based on the provided command-line arguments.

    Args:
        parsed_args (argparse.Namespace): Parsed command line arguments.
    """
    if parsed_args.quiet:
        logging.disable(logging.NOTSET)
        return

    level = logging.DEBUG if parsed_args.debug else logging.INFO
    format_string = (
        "[%(asctime)s] %(levelname)s: %(name)s: %(message)s"
        if parsed_args.debug
        else "%(message)s"
    )

    logging.basicConfig(
        level=level,
        format=format_string,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_or_create_config(
    parsed_args: argparse.Namespace, app: str
) -> Dict[str, Any]:
    """Load configuration from a file or create a new configuration file.

    Args:
        parsed_args: Parsed command line arguments.
        app: Application name to load config for.

    Returns:
        Dict containing merged configuration.

    Raises:
        ConfigFileCorruptedError: If config file is corrupted.
        ConfigFileExistsError: If generating config but file exists.
    """
    if parsed_args.config:
        return _load_config(parsed_args, app)

    if parsed_args.generate_config:
        return _create_config(parsed_args, app)

    return vars(parsed_args)


def _load_config(parsed_args: argparse.Namespace, app: str) -> Dict[str, Any]:
    """Load and validate configuration from a file.

    Args:
        parsed_args: Parsed command line arguments.
        app: Application name.

    Returns:
        Dict containing loaded configuration.

    Raises:
        ConfigFileCorruptedError: If config file is corrupted.
    """
    config_file = parsed_args.config

    with open(config_file, "r", encoding="utf8") as file:
        toml = tomlkit.load(file)

        if len(toml) == 0:
            raise ConfigFileCorruptedError(
                f"Corrupted config file: {config_file}"
            )

        toml_tpl = tomlkit.parse(read_text(__package__, f"{app}.toml"))
        if toml_tpl["config_version"] != toml.get("config_version"):
            _logger.info("Upgrade config file: %s", config_file)
            config = argparse.Namespace(**dict(toml))
            config.generate_config = config_file
            config.config_version = toml_tpl["config_version"]
            return _upgrade_config(config, app)

        _logger.info("Load from config file: %s", config_file)
        for key, value in toml.items():
            _logger.debug("config: %s, value: %s", repr(key), repr(value))

        return toml


def _upgrade_config(config: argparse.Namespace, app: str) -> Dict[str, Any]:
    """Upgrade the configuration file to the latest version.

    Args:
        config: Parsed command line arguments.
        app: Application name.

    Returns:
        Dict containing the upgraded configuration.
    """
    toml_filename = Path(config.generate_config)

    ymd_hms = dt.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = Path(
        toml_filename.resolve().parent.joinpath(
            toml_filename.stem + "_" + ymd_hms + "_backup.toml"
        )
    )
    os.rename(toml_filename, backup_filename)
    _logger.info("Backup config file: %s", backup_filename)

    return _create_config(config, app)


def _create_config(
    parsed_args: argparse.Namespace, app: str
) -> Dict[str, Any]:
    """Create a new configuration file with default values.

    Args:
        parsed_args: Parsed command line arguments.
        app: Application name.

    Returns:
        Dict containing the created configuration.

    Raises:
        ConfigFileExistsError: If a config file already exists.
    """
    config_filename = Path(parsed_args.generate_config)

    if config_filename.exists():
        raise ConfigFileExistsError(
            f"Existing config file found: {config_filename}"
        )

    with open(config_filename, "w", encoding="utf8") as file:
        config_dict = vars(parsed_args)
        _logger.debug(config_dict)

        toml = read_text(__package__, f"{app}.toml")
        doc = tomlkit.parse(toml)

        for key, value in config_dict.items():
            if key in doc:
                doc[key] = value

        file.write(tomlkit.dumps(doc))
        _logger.info("Create config file: %s", config_filename)

        return config_dict


class EnvironmentAction(argparse.Action):
    """Show environment details action."""

    def __init__(self, **kwargs):
        """Initialize the EnvironmentAction."""
        kwargs["nargs"] = 0
        super().__init__(**kwargs)

    def __call__(self, parser, _namespace, _values, option_string=None):
        """Print environment details and exit.

        Args:
            parser: The argument parser.
            namespace: The namespace to store the parsed arguments.
            values: The argument values.
            option_string: The option string that triggered this action.
        """
        sys_version = sys.version.replace("\n", "")
        env = (
            f"xsget: {__version__}\n"
            f"python: {sys_version}\n"
            f"platform: {platform.platform()}\n"
        )
        parser._print_message(env, sys.stdout)
        parser.exit()
