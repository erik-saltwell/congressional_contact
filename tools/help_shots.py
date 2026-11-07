"""Make the help overlay's screenshots from the owner's phone captures.

Reads design_notes/help_screenshots/*.png, crops each to the part that matters,
covers personal details, rings the control to tap, shrinks it and writes a
WebP into src/help-shots/. build.py inlines those files into the page as data
URIs, so the page has no separate image files. Rerun this only when the
captures or the crops change; it needs Pillow (the build itself does not).

    python3 tools/help_shots.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "design_notes" / "help_screenshots"
OUT = ROOT / "src" / "help-shots"

WIDTH = 480          # stored width in pixels: 2x the 240 px the overlay shows
QUALITY = 60         # WebP quality
RING = (242, 107, 29)  # a bright orange that shows on both phones' light and dark screens
RING_W = 12          # ring width in source pixels (about 5 px once shrunk)

# name: (source file, crop box (left, top, right, bottom) in source pixels,
#        rings as boxes, cover boxes filled with a colour sampled beside them)
SHOTS = {
    "android-1": ("android-01-contact-completes-download.png", (0, 150, 1080, 700),
                  [(800, 315, 990, 420)], []),
    "android-2": ("android-02-open-contact.png", (0, 1518, 1080, 2040),
                  [(610, 1730, 1030, 1830)], []),
    "android-3": ("android-03-opened0-in-contacts-with-save-option.png", (0, 1170, 1080, 2300),
                  [(85, 2125, 995, 2290)], [(670, 2015, 760, 2100)]),
    "iphone-1": ("iphone-01-contact-open-after-click-add.png", (0, 175, 1179, 1430), [], []),
    "iphone-2": ("iphone-02-scroll-down-to-create-new-contact.png", (0, 1520, 1179, 2230),
                 [(35, 1880, 1145, 2050)], []),
    "iphone-3": ("iphone-03-contact-created-click-checkmark.png", (0, 175, 1179, 1110),
                 [(975, 200, 1155, 380)], []),
    "iphone-4": ("iphone-04-click-check-to-close-and-finish.png", (0, 175, 1179, 1960),
                 [(25, 200, 205, 380)], []),
}


def make(name, src, crop, rings, covers):
    im = Image.open(SRC / src).convert("RGB")
    d = ImageDraw.Draw(im)
    for box in covers:
        fill = im.getpixel((box[0] - 8, (box[1] + box[3]) // 2))
        d.ellipse(box, fill=fill)
    for box in rings:
        h = box[3] - box[1]
        d.rounded_rectangle(box, radius=h // 2, outline=RING, width=RING_W)
    im = im.crop(crop)
    im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
    path = OUT / f"{name}.webp"
    im.save(path, "WEBP", quality=QUALITY, method=6)
    return path, im.size


def main():
    OUT.mkdir(exist_ok=True)
    total = 0
    for name, spec in SHOTS.items():
        path, size = make(name, *spec)
        total += path.stat().st_size
        print(f"  {path.relative_to(ROOT)}  {size[0]}x{size[1]}  {path.stat().st_size:,} bytes")
    print(f"  total {total:,} bytes (about {total * 4 // 3:,} as base64)")


if __name__ == "__main__":
    main()
