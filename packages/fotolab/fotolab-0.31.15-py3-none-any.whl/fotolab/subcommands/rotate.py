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

"""Rotate subcommand."""

import argparse
import logging

from PIL import Image

from fotolab import save_image

log = logging.getLogger(__name__)


def build_subparser(subparsers) -> None:
    """Build the subparser."""
    rotate_parser = subparsers.add_parser("rotate", help="rotate an image")

    rotate_parser.set_defaults(func=run)

    rotate_parser.add_argument(
        dest="image_filenames",
        help="set the image filenames",
        nargs="+",
        type=str,
        default=None,
        metavar="IMAGE_FILENAMES",
    )

    rotate_parser.add_argument(
        "-r",
        "--rotation",
        type=int,
        default=0,
        help="Rotation angle in degrees (default: '%(default)s')",
    )

    rotate_parser.add_argument(
        "-cw",
        "--clockwise",
        action="store_true",
        help="Rotate clockwise (default: '%(default)s)",
    )

    rotate_parser.add_argument(
        "-op",
        "--open",
        default=False,
        action="store_true",
        dest="open",
        help="open the image using default program (default: '%(default)s')",
    )

    rotate_parser.add_argument(
        "-od",
        "--output-dir",
        dest="output_dir",
        default="output",
        help="set default output folder (default: '%(default)s')",
    )


def run(args: argparse.Namespace) -> None:
    """Run rotate subcommand.

    Args:
        args (argparse.Namespace): Config from command line arguments

    Returns:
        None
    """
    log.debug(args)

    rotation = -args.rotation if args.clockwise else args.rotation
    for image_filename in args.image_filenames:
        original_image = Image.open(image_filename)
        rotated_image = original_image.rotate(
            rotation, expand=True, resample=Image.Resampling.BICUBIC
        )
        save_image(args, rotated_image, image_filename, "rotate")
