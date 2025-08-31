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

"""Sharpen subcommand."""

import argparse
import logging

from PIL import Image, ImageFilter

from fotolab import save_gif_image, save_image

log = logging.getLogger(__name__)


def build_subparser(subparsers) -> None:
    """Build the subparser."""
    sharpen_parser = subparsers.add_parser("sharpen", help="sharpen an image")

    sharpen_parser.set_defaults(func=run)

    sharpen_parser.add_argument(
        dest="image_filenames",
        help="set the image filenames",
        nargs="+",
        type=str,
        default=None,
        metavar="IMAGE_FILENAMES",
    )

    sharpen_parser.add_argument(
        "-r",
        "--radius",
        dest="radius",
        type=int,
        default=1,
        help="set the radius or size of edges (default: '%(default)s')",
        metavar="RADIUS",
    )

    sharpen_parser.add_argument(
        "-p",
        "--percent",
        dest="percent",
        type=int,
        default=100,
        help=(
            "set the amount of overall strength of sharpening effect "
            "(default: '%(default)s')"
        ),
        metavar="PERCENT",
    )

    sharpen_parser.add_argument(
        "-t",
        "--threshold",
        dest="threshold",
        type=int,
        default=3,
        help=(
            "set the minimum brightness changed to be sharpened "
            "(default: '%(default)s')"
        ),
        metavar="THRESHOLD",
    )

    sharpen_parser.add_argument(
        "-ba",
        "--before-after",
        default=False,
        action="store_true",
        dest="before_after",
        help="generate a GIF showing before and after changes",
    )

    sharpen_parser.add_argument(
        "-op",
        "--open",
        default=False,
        action="store_true",
        dest="open",
        help="open the image using default program (default: '%(default)s')",
    )

    sharpen_parser.add_argument(
        "-od",
        "--output-dir",
        dest="output_dir",
        default="output",
        help="set default output folder (default: '%(default)s')",
    )


def run(args: argparse.Namespace) -> None:
    """Run sharpen subcommand.

    Args:
        args (argparse.Namespace): Config from command line arguments

    Returns:
        None
    """
    log.debug(args)

    for image_filename in args.image_filenames:
        original_image = Image.open(image_filename)
        sharpen_image = original_image.filter(
            ImageFilter.UnsharpMask(
                args.radius, percent=args.percent, threshold=args.threshold
            )
        )
        if args.before_after:
            save_gif_image(
                args, image_filename, original_image, sharpen_image, "sharpen"
            )
        else:
            save_image(args, sharpen_image, image_filename, "sharpen")
