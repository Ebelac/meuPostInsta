#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configura a foto de perfil que aparece no header de cada slide.

Aceita:
- Caminho local: /Users/voce/Downloads/foto.jpg
- URL: https://exemplo.com/foto.png
- Drag-drop do Finder/Explorer no terminal (cola o caminho automaticamente)

Uso:
    python3 scripts/setup_profile_photo.py <caminho-ou-url>

Output: assets/profile/profile_photo.png (400x400 crop quadrado centralizado)
"""
import os
import sys
from io import BytesIO

import requests
from PIL import Image


TARGET_SIZE = 400  # 400x400px (recomendado)
OUTPUT_PATH = "assets/profile/profile_photo.png"


def _load_from_source(source: str) -> Image.Image:
    if source.startswith(("http://", "https://")):
        print(f"📥 Baixando: {source}")
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(source, headers=headers, timeout=20)
        r.raise_for_status()
        return Image.open(BytesIO(r.content))

    # Path local — limpa aspas/escapes que vem de drag-drop
    path = source.strip().strip("'\"")
    path = path.replace("\\ ", " ")  # bash escapes em paths com espaco
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo nao encontrado: {path}")
    print(f"📂 Carregando: {path}")
    return Image.open(path)


def _square_crop_center(img: Image.Image, size: int) -> Image.Image:
    img = img.convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    return img.resize((size, size), Image.Resampling.LANCZOS)


def setup_profile_photo(source: str) -> str:
    img = _load_from_source(source)
    img = _square_crop_center(img, TARGET_SIZE)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    img.save(OUTPUT_PATH, "PNG", quality=95, optimize=True)
    print(f"✅ Foto de perfil salva em: {OUTPUT_PATH}")
    print(f"   {TARGET_SIZE}x{TARGET_SIZE}px, crop quadrado centralizado")
    return OUTPUT_PATH


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/setup_profile_photo.py <caminho-ou-url>")
        print("")
        print("Exemplos:")
        print("  python3 scripts/setup_profile_photo.py /Users/voce/Downloads/foto.jpg")
        print("  python3 scripts/setup_profile_photo.py https://exemplo.com/foto.png")
        print("")
        print("Dica: voce pode arrastar o arquivo do Finder direto pro terminal —")
        print("o caminho cola automaticamente.")
        sys.exit(1)

    try:
        setup_profile_photo(sys.argv[1])
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)
