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

"""Border subcommand."""

import argparse
import logging
from typing import Tuple

from PIL import Image, ImageColor, ImageOps

from fotolab import save_image

log = logging.getLogger(__name__)


def build_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Build the subparser."""
    border_parser = subparsers.add_parser("border", help="add border to image")

    border_parser.set_defaults(func=run)

    border_parser.add_argument(
        dest="image_filenames",
        help="set the image filenames",
        nargs="+",
        type=str,
        default=None,
        metavar="IMAGE_FILENAMES",
    )

    border_parser.add_argument(
        "-c",
        "--color",
        dest="color",
        type=str,
        default="black",
        help="set the color of border (default: '%(default)s')",
        metavar="COLOR",
    )

    border_parser.add_argument(
        "-w",
        "--width",
        dest="width",
        type=int,
        default=10,
        help="set the width of border in pixels (default: '%(default)s')",
        metavar="WIDTH",
    )

    border_parser.add_argument(
        "-wt",
        "--width-top",
        dest="width_top",
        type=int,
        default=0,
        help="set the width of top border in pixels (default: '%(default)s')",
        metavar="WIDTH",
    )

    border_parser.add_argument(
        "-wr",
        "--width-right",
        dest="width_right",
        type=int,
        default=0,
        help=(
            "set the width of right border in pixels (default: '%(default)s')"
        ),
        metavar="WIDTH",
    )

    border_parser.add_argument(
        "-wb",
        "--width-bottom",
        dest="width_bottom",
        type=int,
        default=0,
        help=(
            "set the width of bottom border in pixels (default: '%(default)s')"
        ),
        metavar="WIDTH",
    )

    border_parser.add_argument(
        "-wl",
        "--width-left",
        dest="width_left",
        type=int,
        default=0,
        help="set the width of left border in pixels (default: '%(default)s')",
        metavar="WIDTH",
    )

    border_parser.add_argument(
        "-op",
        "--open",
        default=False,
        action="store_true",
        dest="open",
        help="open the image using default program (default: '%(default)s')",
    )

    border_parser.add_argument(
        "-od",
        "--output-dir",
        dest="output_dir",
        default="output",
        help="set default output folder (default: '%(default)s')",
    )


def run(args: argparse.Namespace) -> None:
    """Run border subcommand.

    Args:
        args (argparse.Namespace): Config from command line arguments

    Returns:
        None
    """
    log.debug(args)

    for image_filename in args.image_filenames:
        original_image = Image.open(image_filename)
        border = get_border(args)
        bordered_image = ImageOps.expand(
            original_image,
            border=border,
            fill=ImageColor.getrgb(args.color),
        )

        save_image(args, bordered_image, image_filename, "border")


def get_border(
    args: argparse.Namespace,
) -> Tuple[int, int, int, int]:
    """Calculate the border dimensions.

    Args:
        args (argparse.Namespace): Command line arguments

    Returns:
        Tuple[int, int, int, int]: Border dimensions in pixels as (left, top,
        right, bottom) widths. If individual widths are not specified,
        a uniform width is returned for all sides.
    """
    if any(
        [
            args.width_left,
            args.width_top,
            args.width_right,
            args.width_bottom,
        ]
    ):
        return (
            args.width_left,
            args.width_top,
            args.width_right,
            args.width_bottom,
        )
    # If no individual widths are specified, use the general width for all
    # sides
    return (args.width, args.width, args.width, args.width)
