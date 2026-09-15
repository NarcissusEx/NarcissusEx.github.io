"""Pad an image without stretching or cropping it.

Install: python -m pip install Pillow
Example: python scripts/pad_image.py images/evtrajgs.png --ratio 2:1
"""

import argparse
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageColor, ImageOps


def parse_ratio(value):
    try:
        ratio = Fraction(value.replace(":", "/"))
        if ratio <= 0:
            raise ValueError
        return ratio
    except (ValueError, ZeroDivisionError):
        raise argparse.ArgumentTypeError("Ratio must be positive, e.g. 2:1 or 1.5")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Source image")
    parser.add_argument("--output", type=Path, help="New PNG path (default: <name>_padded.png)")
    parser.add_argument("--ratio", type=parse_ratio, default=parse_ratio("2:1"))
    parser.add_argument("--background", default="white", help="Background color, e.g. white or #ffffff")
    args = parser.parse_args()
    output = args.output or args.input.with_name(args.input.stem + "_padded.png")
    if output.suffix.lower() != ".png":
        parser.error("Output must use the .png extension")
    if output.resolve() == args.input.resolve():
        parser.error("Output must differ from the source image")

    try:
        color = ImageColor.getrgb(args.background)
        with Image.open(args.input) as source:
            picture = ImageOps.exif_transpose(source).convert("RGBA")

        width, height = picture.size
        # Use integer multiples for an exact target ratio, adding pixels only.
        rw, rh = args.ratio.numerator, args.ratio.denominator
        scale = max((width + rw - 1) // rw, (height + rh - 1) // rh)
        target = (scale * rw, scale * rh)
        canvas = Image.new("RGB", target, color)
        left = (target[0] - width) // 2
        top = (target[1] - height) // 2
        canvas.paste(picture, (left, top), picture)

        output.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation prevents accidental replacement of an existing file.
        with output.open("xb") as destination:
            canvas.save(destination, format="PNG")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")

    print(f"Saved: {output}")
    print(f"Image: {width}x{height} -> {target[0]}x{target[1]}")
    print(f"Padding: left={left}, right={target[0] - width - left}, "
          f"top={top}, bottom={target[1] - height - top}")


if __name__ == "__main__":
    main()
