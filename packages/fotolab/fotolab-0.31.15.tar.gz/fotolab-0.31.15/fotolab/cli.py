# Copyright (C) 2024,2025 Kian-Meng Ang

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""A console program to manipulate photos.

website: https://github.com/kianmeng/fotolab
changelog: https://github.com/kianmeng/fotolab/blob/master/CHANGELOG.md
issues: https://github.com/kianmeng/fotolab/issues
"""

import argparse
import logging
import sys
from typing import Optional, Sequence

import fotolab.subcommands
from fotolab import __version__

log = logging.getLogger(__name__)


def setup_logging(args: argparse.Namespace) -> None:
    """Sets up logging configuration based on command-line arguments.

    Args:
        args (argparse.Namespace): Namespace containing parsed arguments.
    """
    if args.quiet:
        logging.disable(logging.NOTSET)
        return

    if args.verbose == 0:
        logging.getLogger("PIL").setLevel(logging.ERROR)

    level = logging.DEBUG if args.debug else logging.INFO
    format_string = (
        "[%(asctime)s] %(levelname)s: %(name)s: %(message)s"
        if args.debug
        else "%(message)s"
    )

    logging.basicConfig(
        level=level,
        format=format_string,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        prog="fotolab",
        description=__doc__,
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(
            prog, max_help_position=20
        ),
    )

    parser.add_argument(
        "-o",
        "--overwrite",
        default=False,
        action="store_true",
        dest="overwrite",
        help="overwrite existing image",
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
        "-v",
        "--verbose",
        default=0,
        action="count",
        dest="verbose",
        help="show verbosity of debugging log, use -vv, -vvv for more details",
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
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(
        help="sub-command help",
        dest="command",
        required=True,
    )
    fotolab.subcommands.build_subparser(subparsers)

    return parser


def main(args: Optional[Sequence[str]] = None) -> None:
    """Run the main program flow."""
    args = args or sys.argv[1:]
    log.debug(args)

    try:
        parser = build_parser()
        parsed_args = parser.parse_args(args)
        setup_logging(parsed_args)

        if parsed_args.command is not None:
            log.debug(parsed_args)
            # Ensure the function attribute exists (set by set_defaults in
            # subcommands)
            if hasattr(parsed_args, "func"):
                parsed_args.func(parsed_args)
            else:
                # This case should ideally not happen if subcommands are set up
                # correctly
                log.error(
                    "subcommand '%s' is missing its execution function.",
                    parsed_args.command,
                )
                parser.print_help(sys.stderr)
                raise SystemExit(1)
        else:
            parser.print_help(sys.stderr)

    except Exception as error:
        log.error(
            "error: %s",
            getattr(error, "message", str(error)),
            exc_info=("-d" in args or "--debug" in args),
        )

        raise SystemExit(1) from None
