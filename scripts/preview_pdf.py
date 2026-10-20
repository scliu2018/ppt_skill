#!/usr/bin/env python3
"""Render selected PDF pages and an indexed contact sheet; requires Poppler and Pillow."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont


def binary(name):
    # A bundled Poppler may require a newer glibc; test before selecting it.
    choices = [shutil.which(name), f'/usr/bin/{name}']
    for path in dict.fromkeys(p for p in choices if p):
        result = subprocess.run([path, '-v'], capture_output=True)
        if result.returncode == 0:
            return path
    raise RuntimeError(f'Working Poppler executable missing: {name}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pages', help='Comma-separated 1-based page numbers; omitted means all pages')
    parser.add_argument('--width', type=int, default=1440)
    args = parser.parse_args()
    if args.width < 400:
        parser.error('--width must be at least 400')
    info = subprocess.check_output([binary('pdfinfo'), str(args.pdf.resolve())], text=True)
    count = int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))
    pages = list(dict.fromkeys(int(p) for p in args.pages.split(','))) if args.pages else list(range(1, count + 1))
    if not pages or any(p < 1 or p > count for p in pages):
        parser.error(f'Page numbers must be within 1..{count}')
    args.output.mkdir(parents=True, exist_ok=True)
    renderer = binary('pdftoppm')
    for p in pages:
        prefix = args.output / f'page-{p:03d}'
        subprocess.run([renderer, '-f', str(p), '-l', str(p), '-singlefile', '-scale-to', str(args.width), '-png', str(args.pdf.resolve()), str(prefix)], check=True, capture_output=True)
    columns, tw, th, pad, label = 3, 480, 300, 16, 30
    rows = (len(pages) + columns - 1) // columns
    sheet = Image.new('RGB', (columns * (tw + pad) + pad, rows * (th + label + pad) + pad), '#e8edf2')
    draw = ImageDraw.Draw(sheet)
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font = ImageFont.truetype(font_path, 18) if Path(font_path).exists() else ImageFont.load_default()
    for i, p in enumerate(pages):
        x, y = pad + (i % columns) * (tw + pad), pad + (i // columns) * (th + label + pad)
        with Image.open(args.output / f'page-{p:03d}.png') as source:
            thumb = source.convert('RGB')
            thumb.thumbnail((tw, th))
            sheet.paste(thumb, (x + (tw - thumb.width) // 2, y))
        draw.text((x, y + th + 3), f'Page {p} / {count}', fill='#17263b', font=font)
    sheet.save(args.output / 'contact-sheet.jpg', quality=90)
    (args.output / 'preview.json').write_text(json.dumps({'source': str(args.pdf.resolve()), 'page_count': count, 'rendered_pages': pages}, indent=2) + '\n')
    print(json.dumps({'pages': count, 'rendered': pages, 'contact_sheet': str(args.output / 'contact-sheet.jpg')}))


if __name__ == '__main__':
    main()
