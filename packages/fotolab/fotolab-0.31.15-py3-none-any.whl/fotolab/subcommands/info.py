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

"""Info subcommand."""

import argparse
import logging

from PIL import ExifTags, Image

log = logging.getLogger(__name__)


def build_subparser(subparsers) -> None:
    """Build the subparser."""
    info_parser = subparsers.add_parser("info", help="info an image")

    info_parser.set_defaults(func=run)

    info_parser.add_argument(
        dest="image_filename",
        help="set the image filename",
        type=str,
        metavar="IMAGE_FILENAME",
    )

    info_parser.add_argument(
        "-s",
        "--sort",
        default=False,
        action="store_true",
        dest="sort",
        help="show image info by sorted field name",
    )

    info_parser.add_argument(
        "--camera",
        default=False,
        action="store_true",
        dest="camera",
        help="show the camera maker details",
    )

    info_parser.add_argument(
        "--datetime",
        default=False,
        action="store_true",
        dest="datetime",
        help="show the datetime",
    )


def run(args: argparse.Namespace) -> None:
    """Run info subcommand.

    Args:
        args (argparse.Namespace): Config from command line arguments

    Returns:
        None
    """
    log.debug(args)

    with Image.open(args.image_filename) as image:
        exif_tags = extract_exif_tags(image, args.sort)

        if not exif_tags:
            print("No metadata found!")
            return

        output_info = []

        if args.camera:
            output_info.append(get_formatted_camera_info(exif_tags))

        if args.datetime:
            output_info.append(get_formatted_datetime_info(exif_tags))

        if output_info:  # Check if any specific info was added
            print("\n".join(output_info))
        else:
            # Print all tags if no specific info was requested
            tag_name_width = max(map(len, exif_tags))
            for tag_name, tag_value in exif_tags.items():
                print(f"{tag_name:<{tag_name_width}}: {tag_value}")


def extract_exif_tags(image: Image.Image, sort: bool = False) -> dict:
    """Extract Exif metadata from image."""
    exif = image.getexif()

    log.debug(exif)

    info = {}
    if exif:
        info = {ExifTags.TAGS.get(tag_id): exif.get(tag_id) for tag_id in exif}

    filtered_info = {
        key: value for key, value in info.items() if key is not None
    }
    if sort:
        filtered_info = dict(sorted(filtered_info.items()))

    return filtered_info


def get_formatted_datetime_info(exif_tags: dict):
    """Extract and format datetime metadata."""
    return exif_tags.get("DateTime", "Not available")


def get_formatted_camera_info(exif_tags: dict):
    """Extract and format camera make and model metadata."""
    make = exif_tags.get("Make", "")
    model = exif_tags.get("Model", "")
    metadata = f"{make} {model}"
    return metadata.strip()
