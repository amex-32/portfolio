#!/usr/bin/env python3
"""Convertit les captures de projets img/*.jpg en WebP : python3 tools/shots.py

Pour chaque capture : <nom>.webp (taille d'origine, 1600 px) et <nom>-800.webp (vignettes, écrans étroits).
Le JPEG d'origine est supprimé. À relancer après l'ajout d'une capture en .jpg dans img/. Demande Pillow.
"""
import pathlib

from PIL import Image

IMG = pathlib.Path(__file__).resolve().parent.parent / "img"

for f in sorted(IMG.glob("*.jpg")):
    im = Image.open(f).convert("RGB")
    im.save(f.with_suffix(".webp"), "WEBP", quality=80, method=6)
    small = im.resize((800, round(im.height * 800 / im.width)), Image.LANCZOS)
    small.save(f.with_name(f.stem + "-800.webp"), "WEBP", quality=78, method=6)
    f.unlink()
    print(f.name, "->", f.stem + ".webp", f.stem + "-800.webp")
