# Copyright (C) 2024,2025 Kian-Meng Ang
#
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

"""Auto subcommand."""

import argparse
import logging

import fotolab.subcommands.contrast
import fotolab.subcommands.resize
import fotolab.subcommands.sharpen
import fotolab.subcommands.watermark

log = logging.getLogger(__name__)


def build_subparser(subparsers) -> None:
    """Build the subparser."""
    auto_parser = subparsers.add_parser(
        "auto", help="auto adjust (resize, contrast, and watermark) a photo"
    )

    auto_parser.set_defaults(func=run)

    auto_parser.add_argument(
        dest="image_filenames",
        help="set the image filename",
        nargs="+",
        type=str,
        default=None,
        metavar="IMAGE_FILENAMES",
    )


def run(args: argparse.Namespace) -> None:
    """Run auto subcommand.

    Args:
        args (argparse.Namespace): Config from command line arguments

    Returns:
        None
    """
    extra_args = {
        "width": 600,
        "height": 277,
        "cutoff": 1,
        "radius": 1,
        "percent": 100,
        "threshold": 2,
        "text": "kianmeng.org",
        "position": "bottom-left",
        "font_size": 12,
        "font_color": "white",
        "outline_width": 2,
        "outline_color": "black",
        "padding": 15,
        "camera": False,
        "canvas": False,
        "lowercase": False,
        "before_after": False,
        "alpha": 128,
    }
    combined_args = argparse.Namespace(**vars(args), **extra_args)
    combined_args.overwrite = True
    combined_args.open = False
    log.debug(args)
    log.debug(combined_args)

    fotolab.subcommands.resize.run(combined_args)
    fotolab.subcommands.contrast.run(combined_args)
    fotolab.subcommands.sharpen.run(combined_args)
    fotolab.subcommands.watermark.run(combined_args)
