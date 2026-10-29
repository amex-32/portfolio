#!/usr/bin/env python3
"""Génère og.png (aperçu des liens partagés), favicon.ico, apple-touch-icon.png et img/bg-blur.webp (fond déjà flouté) : python3 tools/images.py

À relancer seulement si le visuel change. Demande Pillow et une police grasse (FONT_BOLD) et une police à chasse fixe (FONT_MONO).
"""
import pathlib
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT_BOLD = sys.argv[1] if len(sys.argv) > 1 else "C:/Windows/Fonts/segoeuib.ttf"
FONT_MONO = sys.argv[2] if len(sys.argv) > 2 else "C:/Windows/Fonts/consola.ttf"
ACCENT, VIOLET, BG1, BG2, TEXT, TEXT2 = (124, 196, 255), (155, 140, 255), (13, 23, 38), (8, 12, 22), (241, 245, 251), (166, 180, 198)


def gradient(w, h, a, b):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            k = (x / w + y / h) / 2
            px[x, y] = tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3))
    return img


def monogram(size):
    """Pastille « AK » du site (même dégradé que l'avatar)."""
    img = gradient(size, size, ACCENT, VIOLET).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=size // 4, fill=255)
    img.putalpha(mask)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_BOLD, int(size * .46))
    d.text((size / 2, size / 2), "AK", font=f, fill=BG1, anchor="mm")
    return img


def og_card(title, sub="Alexandre K. · Portfolio"):
    """Aperçu de lien (1200 × 630) : le titre de la page sur le fond du site."""
    og = gradient(1200, 630, BG1, BG2)
    d = ImageDraw.Draw(og)
    for x in range(0, 1200, 40):
        d.line((x, 0, x, 630), fill=(20, 32, 50))
    for y in range(0, 630, 40):
        d.line((0, y, 1200, y), fill=(20, 32, 50))
    og.paste(monogram(132), (90, 90), monogram(132))
    size = 96
    while d.textlength(title, font=ImageFont.truetype(FONT_BOLD, size)) > 1020 and size > 40:
        size -= 4  # un long titre rétrécit pour tenir dans la largeur
    d.text((90, 280), title, font=ImageFont.truetype(FONT_BOLD, size), fill=TEXT)
    d.text((94, 400), sub, font=ImageFont.truetype(FONT_BOLD, 40), fill=ACCENT)
    d.text((94, 500), "$ projets · write-ups · mini-CTF", font=ImageFont.truetype(FONT_MONO, 32), fill=TEXT2)
    return og


def bg_blur():
    """Fond du site flouté une fois pour toutes : un filter: blur() sur un calque plein écran coûte à chaque image dans Firefox."""
    img = Image.open(ROOT / "img/bg.webp").convert("RGB")
    img = ImageEnhance.Color(img.filter(ImageFilter.GaussianBlur(12))).enhance(1.1)
    return img.crop((24, 14, img.width - 24, img.height - 14))  # bords bavés du flou retirés, comme le scale(1.08) d'avant


if __name__ == "__main__":
    bg_blur().save(ROOT / "img/bg-blur.webp", quality=80)
    og_card("Alexandre K.", "Étudiant en cybersécurité · Portfolio").save(ROOT / "og.png", optimize=True)
    monogram(180).save(ROOT / "apple-touch-icon.png", optimize=True)
    monogram(64).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print("ok")
