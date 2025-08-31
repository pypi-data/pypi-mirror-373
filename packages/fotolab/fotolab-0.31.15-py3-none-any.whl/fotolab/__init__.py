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

"""A console program that manipulate images."""

import argparse
import logging
import os
import subprocess
import sys
from importlib import metadata
from pathlib import Path

from PIL import Image

__version__ = metadata.version("fotolab")

log = logging.getLogger(__name__)


def save_gif_image(
    args: argparse.Namespace,
    image_filename: str,
    original_image: Image.Image,
    after_image: Image.Image,
    subcommand: str,
) -> None:
    """Save the original and after image."""
    image_file = Path(image_filename)
    new_filename = Path(
        args.output_dir,
        image_file.with_name(f"{subcommand}_gif_{image_file.stem}.gif"),
    )
    new_filename.parent.mkdir(parents=True, exist_ok=True)

    log.info("%s gif image: %s", subcommand, new_filename)
    original_image.save(
        new_filename,
        format="gif",
        append_images=[after_image],
        save_all=True,
        duration=2500,
        loop=0,
        optimize=True,
    )

    if args.open:
        _open_image(new_filename)


def save_image(
    args: argparse.Namespace,
    new_image: Image.Image,
    output_filename: str,
    subcommand: str,
) -> None:
    """Save image after image operation.

    Returns:
        None
    """
    image_file = Path(output_filename)
    new_filename = _get_output_filename(args, image_file, subcommand)
    log.info("%s image: %s", subcommand, new_filename.resolve())
    new_image.save(new_filename)

    if args.open:
        _open_image(new_filename)


def _get_output_filename(
    args: argparse.Namespace, image_file: Path, subcommand: str
) -> Path:
    """Build and return output filename based on the command line options."""
    if args.overwrite:
        return image_file.with_name(image_file.name)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / image_file.with_name(f"{subcommand}_{image_file.name}")


def _open_image(filename):
    """Open generated image using default program."""
    try:
        if sys.platform == "linux":
            subprocess.call(["xdg-open", filename])
        elif sys.platform == "darwin":
            subprocess.call(["open", filename])
        elif sys.platform == "win32":
            os.startfile(filename)
        log.info("open image: %s", filename.resolve())

    except (OSError, FileNotFoundError) as error:
        log.error("Error opening image: %s -> %s", filename, error)
