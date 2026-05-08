#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera um contact sheet 3x3 dos 9 slides de um carrossel.

Uso:
    python3 scripts/build_contact_sheet.py <tema>

Input:  assets/generated_carousels/<tema>_slide_01..09.png
Output: assets/generated_carousels/<tema>_contact_sheet.png

Util pra revisar visualmente o carrossel inteiro de uma vez (numa imagem so),
mandar pelo WhatsApp/Telegram pra revisar no celular antes de postar.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont


THUMB_W = 360
THUMB_H = 480
GAP = 14
MARGIN = 28
LABEL_H = 28
COLS = 3
ROWS = 3
BG_COLOR = "#F0F2F5"
LABEL_COLOR = "#202428"
LABEL_BG = "#FFFFFF"
BORDER_COLOR = "#9AA5B1"


def _load_label_font(size: int = 22):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def build_contact_sheet(tema: str) -> str:
    src_dir = "assets/generated_carousels"
    paths = [
        os.path.join(src_dir, f"{tema}_slide_{i:02d}.png") for i in range(1, 10)
    ]
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        print(f"❌ Faltam slides:")
        for p in missing:
            print(f"   {p}")
        sys.exit(1)

    cell_h = THUMB_H + LABEL_H
    sheet_w = COLS * THUMB_W + (COLS - 1) * GAP + 2 * MARGIN
    sheet_h = ROWS * cell_h + (ROWS - 1) * GAP + 2 * MARGIN

    sheet = Image.new("RGB", (sheet_w, sheet_h), color=BG_COLOR)
    draw = ImageDraw.Draw(sheet)
    font = _load_label_font(22)

    for idx, path in enumerate(paths):
        row = idx // COLS
        col = idx % COLS
        x = MARGIN + col * (THUMB_W + GAP)
        y = MARGIN + row * (cell_h + GAP)

        # Thumbnail do slide
        thumb = Image.open(path).convert("RGB").resize(
            (THUMB_W, THUMB_H), Image.Resampling.LANCZOS
        )
        sheet.paste(thumb, (x, y))

        # Borda
        draw.rectangle(
            [x, y, x + THUMB_W, y + THUMB_H],
            outline=BORDER_COLOR,
            width=1,
        )

        # Label (numero do slide) abaixo do thumb
        label_y = y + THUMB_H
        draw.rectangle(
            [x, label_y, x + THUMB_W, label_y + LABEL_H],
            fill=LABEL_BG,
            outline=BORDER_COLOR,
            width=1,
        )
        draw.text(
            (x + THUMB_W / 2, label_y + LABEL_H / 2),
            f"Slide {idx + 1}",
            font=font,
            fill=LABEL_COLOR,
            anchor="mm",
        )

    out_path = os.path.join(src_dir, f"{tema}_contact_sheet.png")
    sheet.save(out_path, "PNG", quality=95, optimize=True)
    print(f"✅ Contact sheet salvo: {out_path}")
    print(f"   Dimensoes: {sheet_w}x{sheet_h}px")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/build_contact_sheet.py <tema>")
        print("Exemplo: python3 scripts/build_contact_sheet.py windows_foguete")
        sys.exit(1)
    build_contact_sheet(sys.argv[1])
