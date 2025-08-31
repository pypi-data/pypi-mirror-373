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

"""Watermark subcommand."""

import argparse
import logging
import math
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageSequence

from fotolab import save_image
from fotolab.subcommands.info import get_formatted_camera_info

log: logging.Logger = logging.getLogger(__name__)

FONT_SIZE_ASPECT_RATIO: float = 12 / 600
FONT_PADDING_ASPECT_RATIO: float = 15 / 600
FONT_OUTLINE_WIDTH_ASPECT_RATIO: float = 2 / 600
POSITIONS: list[str] = ["top-left", "top-right", "bottom-left", "bottom-right"]


def build_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Build the subparser."""
    watermark_parser: argparse.ArgumentParser = subparsers.add_parser(
        "watermark", help="watermark an image"
    )

    watermark_parser.set_defaults(func=run)

    watermark_parser.add_argument(
        dest="image_filenames",
        help="set the image filenames",
        nargs="+",
        type=str,
        default=None,
        metavar="IMAGE_FILENAMES",
    )

    watermark_parser.add_argument(
        "-t",
        "--text",
        dest="text",
        help="set the watermark text (default: '%(default)s')",
        type=str,
        default="kianmeng.org",
        metavar="WATERMARK_TEXT",
    )

    watermark_parser.add_argument(
        "-p",
        "--position",
        dest="position",
        choices=POSITIONS,
        help="set position of the watermark text (default: '%(default)s')",
        default="bottom-left",
    )

    watermark_parser.add_argument(
        "-pd",
        "--padding",
        dest="padding",
        type=int,
        default=15,
        help=(
            "set the padding of the watermark text relative to the image "
            "(default: '%(default)s')"
        ),
        metavar="PADDING",
    )

    watermark_parser.add_argument(
        "-fs",
        "--font-size",
        dest="font_size",
        type=int,
        default=12,
        help="set the font size of watermark text (default: '%(default)s')",
        metavar="FONT_SIZE",
    )

    watermark_parser.add_argument(
        "-fc",
        "--font-color",
        dest="font_color",
        type=str,
        default="white",
        help="set the font color of watermark text (default: '%(default)s')",
        metavar="FONT_COLOR",
    )

    watermark_parser.add_argument(
        "-ow",
        "--outline-width",
        dest="outline_width",
        type=int,
        default=2,
        help=(
            "set the outline width of the watermark text (default: '%(default)s')"
        ),
        metavar="OUTLINE_WIDTH",
    )

    watermark_parser.add_argument(
        "-oc",
        "--outline-color",
        dest="outline_color",
        type=str,
        default="black",
        help=(
            "set the outline color of the watermark text (default: '%(default)s')"
        ),
        metavar="OUTLINE_COLOR",
    )

    watermark_parser.add_argument(
        "-a",
        "--alpha",
        dest="alpha",
        type=int,
        default=128,
        choices=range(0, 256),
        metavar="ALPHA_VALUE",
        help=(
            "set the transparency of the watermark text (0-255, "
            "where 0 is fully transparent and 255 is fully opaque; "
            "default: '%(default)s')"
        ),
    )

    watermark_parser.add_argument(
        "--camera",
        default=False,
        action="store_true",
        dest="camera",
        help="use camera metadata as watermark",
    )

    watermark_parser.add_argument(
        "-l",
        "--lowercase",
        default=True,
        action=argparse.BooleanOptionalAction,
        dest="lowercase",
        help="lowercase the watermark text",
    )

    watermark_parser.add_argument(
        "-op",
        "--open",
        default=False,
        action="store_true",
        dest="open",
        help="open the image using default program (default: '%(default)s')",
    )

    watermark_parser.add_argument(
        "-od",
        "--output-dir",
        dest="output_dir",
        default="output",
        help="set default output folder (default: '%(default)s')",
    )


def run(args: argparse.Namespace) -> None:
    """Run watermark subcommand.

    Args:
        args (argparse.Namespace): Config from command line arguments

    Returns:
        None
    """
    log.debug(args)

    for image_filename in args.image_filenames:
        try:
            image: Image.Image = Image.open(image_filename)
        except FileNotFoundError:
            log.error("Image file not found: %s", image_filename)
            continue
        except Exception as e:
            log.error("Could not open image %s: %s", image_filename, e)
            continue

        if image.format == "GIF":
            watermark_gif_image(image, image_filename, args)
        else:
            watermarked_image: Image.Image = watermark_non_gif_image(
                image, args
            )
            save_image(args, watermarked_image, image_filename, "watermark")


def watermark_gif_image(
    original_image: Image.Image, output_filename: str, args: argparse.Namespace
) -> None:
    """Watermark a GIF image.

    Args:
        original_image (Image.Image): The original GIF image
        output_filename (str): Path to save the watermarked GIF
        args (argparse.Namespace): Command line arguments

    Returns:
        None
    """
    frames: list[Image.Image] = []
    for frame in ImageSequence.Iterator(original_image):
        watermarked_frame: Image.Image = watermark_image(
            args, frame.convert("RGBA"), args.alpha
        )
        frames.append(watermarked_frame)

    image_file: Path = Path(output_filename)

    if args.overwrite:
        new_filename: Path = image_file.with_name(image_file.name)
    else:
        new_filename = Path(
            args.output_dir,
            image_file.with_name(f"watermark_{image_file.name}"),
        )
        new_filename.parent.mkdir(parents=True, exist_ok=True)

    log.info("%s image: %s", "watermark", new_filename.resolve())

    frames[0].save(
        new_filename,
        save_all=True,
        append_images=frames[1:],
        duration=original_image.info.get("duration", 100),
        loop=original_image.info.get("loop", 0),
        disposal=original_image.info.get("disposal", 2),
    )


def watermark_non_gif_image(
    original_image: Image.Image, args: argparse.Namespace
) -> Image.Image:
    """Watermark a non-GIF image.

    Args:
        original_image (Image.Image): The original image
        args (argparse.Namespace): Command line arguments

    Returns:
        Image.Image: The watermarked image
    """
    return watermark_image(args, original_image, args.alpha)


def watermark_image(
    args: argparse.Namespace, original_image: Image.Image, alpha: int
) -> Image.Image:
    """Watermark an image."""
    watermarked_image: Image.Image = original_image.copy()
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(watermarked_image)

    font: ImageFont.FreeTypeFont = ImageFont.load_default(
        calc_font_size(original_image, args)
    )
    log.debug("default font: %s", " ".join(font.getname()))

    text: str = prepare_text(args, original_image)
    (left, top, right, bottom) = draw.textbbox(xy=(0, 0), text=text, font=font)
    text_width: int = right - left
    text_height: int = bottom - top
    (position_x, position_y) = calc_position(
        watermarked_image,
        text_width,
        text_height,
        args.position,
        calc_padding(original_image, args),
    )

    try:
        font_fill_color = ImageColor.getrgb(args.font_color)
        stroke_fill_color = ImageColor.getrgb(args.outline_color)
    except ValueError:
        log.error("Invalid font or outline color specified. Using defaults.")
        font_fill_color = ImageColor.getrgb("white")
        stroke_fill_color = ImageColor.getrgb("black")

    draw.text(
        (position_x, position_y),
        text,
        font=font,
        fill=(*font_fill_color, alpha),
        stroke_width=calc_font_outline_width(original_image, args),
        stroke_fill=(*stroke_fill_color, alpha),
    )
    return watermarked_image


def prepare_text(args: argparse.Namespace, image: Image.Image) -> str:
    """Prepare the watermark text."""
    text = args.text
    if args.camera:
        metadata_text = get_formatted_camera_info(image)
        if metadata_text:
            text = metadata_text
        else:
            log.warning(
                "Camera metadata requested but not found or empty; "
                "falling back to default text: '%s'",
                args.text,
            )

    if args.lowercase:
        text = text.lower()

    return text


def calc_font_size(image: Image.Image, args: argparse.Namespace) -> int:
    """Calculate the font size based on the width of the image."""
    width, _height = image.size
    new_font_size: int = args.font_size
    if width > 600:
        new_font_size = math.floor(FONT_SIZE_ASPECT_RATIO * width)

    log.debug("new font size: %d", new_font_size)
    return new_font_size


def calc_font_outline_width(
    image: Image.Image, args: argparse.Namespace
) -> int:
    """Calculate the font padding based on the width of the image."""
    width, _height = image.size
    new_font_outline_width: int = args.outline_width
    if width > 600:
        new_font_outline_width = math.floor(
            FONT_OUTLINE_WIDTH_ASPECT_RATIO * width
        )

    log.debug("new font outline width: %d", new_font_outline_width)
    return new_font_outline_width


def calc_padding(image: Image.Image, args: argparse.Namespace) -> int:
    """Calculate the font padding based on the width of the image."""
    width, _height = image.size
    new_padding: int = args.padding
    if width > 600:
        new_padding = math.floor(FONT_PADDING_ASPECT_RATIO * width)

    log.debug("new padding: %d", new_padding)
    return new_padding


def calc_position(
    image: Image.Image,
    text_width: int,
    text_height: int,
    position: str,
    padding: int,
) -> Tuple[int, int]:
    """Calculate the boundary coordinates of the watermark text."""
    positions: dict[str, Tuple[int, int]] = {
        "top-left": (padding, padding),
        "top-right": (image.width - text_width - padding, padding),
        "bottom-left": (padding, image.height - text_height - padding),
        "bottom-right": (
            image.width - text_width - padding,
            image.height - text_height - padding,
        ),
    }

    return positions.get(position, (0, 0))
