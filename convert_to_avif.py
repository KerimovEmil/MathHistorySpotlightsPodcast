#!/usr/bin/env python3
"""
Convert PNG / JPG images to modern .avif format.

Usage:
    python convert_to_avif.py path/to/image.png
    python convert_to_avif.py path/to/image.png --output path/to/output.avif --quality 80
    python convert_to_avif.py --batch assets/images/episodes/
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def convert_image_to_avif(
    input_path: Path,
    output_path: Path = None,
    quality: int = 80,
    max_dim: int = None,
) -> bool:
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        print(f"[ERROR] File not found: {input_path}")
        return False

    if output_path is None:
        output_path = input_path.with_suffix(".avif")
    else:
        output_path = Path(output_path).resolve()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Method 1: Pillow + pillow_avif / pillow_heif
    try:
        try:
            import pillow_avif  # registers AVIF plugin for Pillow
        except ImportError:
            pass

        try:
            import pillow_heif
            pillow_heif.register_avif_opener()
        except ImportError:
            pass

        from PIL import Image

        with Image.open(input_path) as img:
            # Handle color channels
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img_conv = img.convert("RGBA")
            else:
                img_conv = img.convert("RGB")

            # Optional downscaling
            if max_dim and (img_conv.width > max_dim or img_conv.height > max_dim):
                img_conv.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

            img_conv.save(str(output_path), format="AVIF", quality=quality)

        orig_kb = input_path.stat().st_size / 1024
        new_kb = output_path.stat().st_size / 1024
        savings = (1 - (new_kb / orig_kb)) * 100 if orig_kb > 0 else 0
        print(f"[SUCCESS - Pillow] Converted {input_path.name} -> {output_path.name}")
        print(f"                  Original: {orig_kb:.1f} KB -> AVIF: {new_kb:.1f} KB ({savings:.1f}% reduction)")
        return True
    except Exception as e:
        print(f"[Pillow Notice] Pillow conversion failed: {e}")

    # Method 2: ImageMagick fallback
    if shutil.which("magick"):
        try:
            cmd = ["magick", str(input_path), "-quality", str(quality), str(output_path)]
            subprocess.run(cmd, check=True)
            orig_kb = input_path.stat().st_size / 1024
            new_kb = output_path.stat().st_size / 1024
            savings = (1 - (new_kb / orig_kb)) * 100 if orig_kb > 0 else 0
            print(f"[SUCCESS - ImageMagick] Converted {input_path.name} -> {output_path.name}")
            print(f"                       Original: {orig_kb:.1f} KB -> AVIF: {new_kb:.1f} KB ({savings:.1f}% reduction)")
            return True
        except Exception as e:
            print(f"[ImageMagick Notice] ImageMagick conversion failed: {e}")

    print(f"[FAILURE] Could not convert {input_path} to .avif")
    return False


def main():
    parser = argparse.ArgumentParser(description="Convert PNG/JPG to AVIF")
    parser.add_argument("input", nargs="?", default=None, help="Input image file path")
    parser.add_argument("--output", "-o", default=None, help="Output .avif file path")
    parser.add_argument("--quality", "-q", type=int, default=80, help="AVIF Quality (1-100, default 80)")
    parser.add_argument("--max-dim", type=int, default=None, help="Optional max dimension for resizing")
    parser.add_argument("--batch", "-b", help="Directory path to batch convert all PNG/JPG files")

    args = parser.parse_args()

    if args.batch:
        batch_dir = Path(args.batch).resolve()
        if not batch_dir.is_dir():
            print(f"[ERROR] Directory not found: {batch_dir}")
            sys.exit(1)
        
        image_files = list(batch_dir.glob("*.png")) + list(batch_dir.glob("*.jpg")) + list(batch_dir.glob("*.jpeg"))
        print(f"Found {len(image_files)} images in {batch_dir}")
        for img_path in image_files:
            convert_image_to_avif(img_path, quality=args.quality, max_dim=args.max_dim)
    elif args.input:
        convert_image_to_avif(Path(args.input), Path(args.output) if args.output else None, quality=args.quality, max_dim=args.max_dim)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
