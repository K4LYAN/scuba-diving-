# -*- coding: utf-8 -*-
"""
Dive Adda — image pipeline.

    python tools/optimize_images.py

Brochure photos: writes WebP renditions at the widths pages actually request
(640 for phones, the native width for everything larger) next to the original
JPEG, which stays as the fallback. A manifest records the widths so
build_site.py can emit matching srcset/sizes.

Logos and badges: the sources are 500-900px wide but render at 56-168px, so
retina-sized PNGs are written alongside them, plus favicon / touch icons.
Originals are never modified.
"""
import json
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'assets', 'img')
BROCHURE = os.path.join(IMG, 'brochure')
PHONE_W = 640
QUALITY = 80


def kb(path):
    return os.path.getsize(path) / 1024.0


PHOTO_DIRS = [BROCHURE, os.path.join(IMG, 'activities')]


def optimize_dir(folder):
    """WebP renditions (phone, mid, native width) next to each JPEG, plus a manifest."""
    manifest = {}
    for name in sorted(os.listdir(folder)):
        if not name.endswith('.jpg'):
            continue
        stem = name[:-4]
        src = os.path.join(folder, name)
        im = Image.open(src).convert('RGB')
        widths = sorted({min(PHONE_W, im.width), min(1024, im.width), im.width})
        for w in widths:
            h = round(im.height * w / im.width)
            out = os.path.join(folder, '%s-%d.webp' % (stem, w))
            (im if w == im.width else im.resize((w, h), Image.LANCZOS)).save(out, 'WEBP', quality=QUALITY, method=6)
        manifest[stem] = {'w': im.width, 'h': im.height, 'widths': widths}
        largest = os.path.join(folder, '%s-%d.webp' % (stem, im.width))
        print('  %-26s jpg %6.1f KB -> webp %6.1f KB  (%s)' % (name, kb(src), kb(largest), ', '.join(map(str, widths))))
    with open(os.path.join(folder, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=1, sort_keys=True)


def resized_png(src_name, out_name, width):
    src = os.path.join(IMG, src_name)
    im = Image.open(src).convert('RGBA')
    h = round(im.height * width / im.width)
    out = os.path.join(IMG, out_name)
    im.resize((width, h), Image.LANCZOS).save(out, 'PNG', optimize=True)
    print('  %-26s %6.1f KB -> %-28s %6.1f KB  (%dx%d)' % (src_name, kb(src), out_name, kb(out), width, h))
    return width, h


def icon(size, out_name, background=None):
    im = Image.open(os.path.join(IMG, 'logo-mark.png')).convert('RGBA')
    canvas = Image.new('RGBA', (size, size), background or (0, 0, 0, 0))
    pad = round(size * (0.14 if background else 0.04))
    box = size - pad * 2
    scale = min(box / im.width, box / im.height)
    mark = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    canvas.alpha_composite(mark, ((size - mark.width) // 2, (size - mark.height) // 2))
    out = os.path.join(IMG, out_name)
    (canvas.convert('RGB') if background else canvas).save(out, 'PNG', optimize=True)
    print('  %-26s %6.1f KB' % (out_name, kb(out)))


def main():
    for folder in PHOTO_DIRS:
        print('Photos in', os.path.relpath(folder, ROOT))
        optimize_dir(folder)
    print('Logos (retina sizes of how they are displayed)')
    resized_png('logo-mark-light.png', 'logo-mark-light-2x.png', 168)   # nav: 38px tall
    resized_png('logo-mark.png', 'logo-mark-2x.png', 168)
    resized_png('logo-full-light.png', 'logo-full-light-2x.png', 336)   # footer: 168px wide
    resized_png('logo-full.png', 'logo-full-2x.png', 336)
    resized_png('ssi-dive-center.png', 'ssi-dive-center-2x.png', 264)   # badge: up to 132px
    print('Icons')
    icon(64, 'favicon-64.png')
    icon(180, 'apple-touch-icon.png', background=(4, 18, 31, 255))


if __name__ == '__main__':
    main()
