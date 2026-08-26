# Copyright (C) @itsSmartDev

from __future__ import annotations

import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

try:
    import numpy as _np
except Exception:
    _np = None


W, H = 1536, 1024
MARGIN = 40
GAP = 24

FONT_CANDIDATES = {
    "display_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansDisplay-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "display_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansDisplay-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "sans_regular": [
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "sans_bold": [
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "bn_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "bn_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "deva_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "deva_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "guru_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansGurmukhi-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "guru_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansGurmukhi-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "gujr_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansGujarati-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "gujr_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansGujarati-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "orya_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansOriya-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "orya_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansOriya-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "taml_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "taml_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansTamil-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "telu_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansTelugu-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "telu_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansTelugu-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "knda_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "knda_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansKannada-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "mlym_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "mlym_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "sinh_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansSinhala-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "sinh_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansSinhala-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "thai_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "thai_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "lao_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansLao-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "lao_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansLao-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "mymr_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansMyanmar-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "mymr_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansMyanmar-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "khmr_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansKhmer-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "khmr_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansKhmer-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "arab_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "arab_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "hebr_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "hebr_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansHebrew-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "armn_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansArmenian-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "armn_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansArmenian-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "geor_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansGeorgian-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "geor_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansGeorgian-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "ethi_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansEthiopic-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "ethi_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansEthiopic-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "cjk": [
        "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "mono": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    ],
    "emoji": [
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "old_italic": [
        "/usr/share/fonts/truetype/noto/NotoSansOldItalic-Regular.ttf",
        "/usr/share/fonts/truetype/unifont/unifont.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "math_fraktur": [
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "math_sans": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "symbol": [
        "/usr/share/fonts/truetype/unifont/unifont.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansSymbols2-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
}

_BUNDLED_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "assets", "fonts")


def _with_bundled(candidates: list[str]) -> list[str]:
    out: list[str] = []
    for path in candidates:
        bundled = os.path.join(_BUNDLED_FONT_DIR, os.path.basename(path))
        out.append(bundled)
        out.append(path)
    return out


FONT_CANDIDATES = {name: _with_bundled(paths) for name, paths in FONT_CANDIDATES.items()}

PALETTE = {
    "bg0": (5, 8, 22),
    "bg1": (12, 16, 34),
    "card": (10, 15, 31),
    "card2": (15, 21, 42),
    "muted": (151, 163, 184),
    "text": (244, 247, 251),
    "line": (79, 93, 124),
    "violet": (139, 92, 246),
    "cyan": (34, 211, 238),
    "pink": (236, 72, 153),
    "green": (74, 222, 128),
    "gold": (245, 196, 81),
    "silver": (203, 213, 225),
    "bronze": (217, 119, 87),
}


def font_path(name: str) -> str:
    for path in FONT_CANDIDATES[name]:
        if Path(path).exists():
            return path
    for fallback in (
        os.path.join(_BUNDLED_FONT_DIR, "DejaVuSans.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(fallback).exists():
            return fallback
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


_font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def f(name: str, size: int) -> ImageFont.FreeTypeFont:
    key = (name, size)
    font = _font_cache.get(key)
    if font is None:
        font = ImageFont.truetype(font_path(name), size=size, layout_engine=ImageFont.Layout.RAQM)
        _font_cache[key] = font
    return font


def bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


SCRIPT_RANGES = {
    "armn": [(0x0530, 0x058F)],
    "hebr": [(0x0590, 0x05FF)],
    "arab": [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)],
    "deva": [(0x0900, 0x097F)],
    "bn": [(0x0980, 0x09FF)],
    "guru": [(0x0A00, 0x0A7F)],
    "gujr": [(0x0A80, 0x0AFF)],
    "orya": [(0x0B00, 0x0B7F)],
    "taml": [(0x0B80, 0x0BFF)],
    "telu": [(0x0C00, 0x0C7F)],
    "knda": [(0x0C80, 0x0CFF)],
    "mlym": [(0x0D00, 0x0D7F)],
    "sinh": [(0x0D80, 0x0DFF)],
    "thai": [(0x0E00, 0x0E7F)],
    "lao": [(0x0E80, 0x0EFF)],
    "mymr": [(0x1000, 0x109F), (0xAA60, 0xAA7F)],
    "geor": [(0x10A0, 0x10FF)],
    "ethi": [(0x1200, 0x137F), (0x1380, 0x139F), (0x2D80, 0x2DDF), (0xAB00, 0xAB2F)],
    "khmr": [(0x1780, 0x17FF), (0x19E0, 0x19FF)],
    "cjk": [
        (0x2E80, 0x303F), (0x3040, 0x30FF), (0x31F0, 0x31FF),
        (0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xAC00, 0xD7AF),
        (0x1100, 0x11FF), (0x3130, 0x318F), (0xF900, 0xFAFF), (0xFF00, 0xFFEF),
    ],
}


SCRIPT_FONTS = {
    "armn": ("armn_regular", "armn_bold"),
    "hebr": ("hebr_regular", "hebr_bold"),
    "arab": ("arab_regular", "arab_bold"),
    "deva": ("deva_regular", "deva_bold"),
    "bn": ("bn_regular", "bn_bold"),
    "guru": ("guru_regular", "guru_bold"),
    "gujr": ("gujr_regular", "gujr_bold"),
    "orya": ("orya_regular", "orya_bold"),
    "taml": ("taml_regular", "taml_bold"),
    "telu": ("telu_regular", "telu_bold"),
    "knda": ("knda_regular", "knda_bold"),
    "mlym": ("mlym_regular", "mlym_bold"),
    "sinh": ("sinh_regular", "sinh_bold"),
    "thai": ("thai_regular", "thai_bold"),
    "lao": ("lao_regular", "lao_bold"),
    "mymr": ("mymr_regular", "mymr_bold"),
    "geor": ("geor_regular", "geor_bold"),
    "ethi": ("ethi_regular", "ethi_bold"),
    "khmr": ("khmr_regular", "khmr_bold"),
    "cjk": ("cjk", "cjk"),
}


def script_of(ch: str) -> str | None:
    cp = ord(ch)
    for kind, ranges in SCRIPT_RANGES.items():
        for lo, hi in ranges:
            if lo <= cp <= hi:
                return kind
    return None


def is_emoji_char(ch: str) -> bool:
    cp = ord(ch)
    return 0x1F000 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF or 0x1F1E6 <= cp <= 0x1F1FF or ch in {"♾", "∞"}


def run_type(ch: str) -> str:
    cp = ord(ch)
    if ch in {"\ufe0f", "\u200d"} or is_emoji_char(ch):
        return "emoji"
    if 0x10300 <= cp <= 0x1032F:
        return "old_italic"
    if 0x1D56C <= cp <= 0x1D59F:
        return "math_fraktur"
    if 0x1D400 <= cp <= 0x1D7FF:
        return "math_sans"
    if 0x2300 <= cp <= 0x23FF:
        return "symbol"
    s = script_of(ch)
    if s is not None:
        return s
    return "latin"


def split_runs(text: str) -> list[tuple[str, str]]:
    runs: list[tuple[str, str]] = []
    cur = ""
    cur_type = ""
    for ch in text:
        typ = run_type(ch)
        if typ == "emoji" and ch in {"\ufe0f", "\u200d"} and cur:
            cur += ch
            continue
        if cur and typ != cur_type:
            runs.append((cur, cur_type))
            cur = ch
        else:
            cur += ch
        cur_type = typ
    if cur:
        runs.append((cur, cur_type))
    return runs


def text_font(kind: str, size: int, weight: str) -> ImageFont.FreeTypeFont:
    if kind in SCRIPT_FONTS:
        regular, bold = SCRIPT_FONTS[kind]
        return f(bold if weight == "bold" else regular, size)
    if kind in {"old_italic", "math_fraktur", "math_sans", "symbol"}:
        return f(kind, size)
    return f("sans_bold" if weight == "bold" else "sans_regular", size)


def emoji_image(text: str, target_h: int) -> Image.Image | None:
    try:
        emoji_font = f("emoji", 109)
        temp = Image.new("RGBA", (220, 180), (0, 0, 0, 0))
        td = ImageDraw.Draw(temp)
        td.text((6, 8), text, font=emoji_font, embedded_color=True)
        box = temp.getbbox()
        if not box:
            return None
        crop = temp.crop(box)
        scale = target_h / max(1, crop.height)
        return crop.resize((max(1, int(crop.width * scale)), target_h), Image.Resampling.LANCZOS)
    except Exception:
        return None


def measure_mixed(draw: ImageDraw.ImageDraw, text: str, size: int, weight: str = "regular") -> tuple[int, int]:
    width = 0
    height = 0
    for run, kind in split_runs(text):
        if kind == "emoji":
            img = emoji_image(run, int(size * 1.05))
            w, h = (img.width, img.height) if img else (size, size)
        else:
            w, h = bbox(draw, run, text_font(kind, size, weight))
        width += w
        height = max(height, h)
    return width, height


def ellipsize(draw: ImageDraw.ImageDraw, text: str, size: int, weight: str, max_w: int) -> str:
    if measure_mixed(draw, text, size, weight)[0] <= max_w:
        return text
    out = text.rstrip()
    while out and measure_mixed(draw, out + "…", size, weight)[0] > max_w:
        out = out[:-1].rstrip()
    return out + "…" if out else "…"


def draw_mixed(base: Image.Image, xy: tuple[int, int], text: str, size: int, fill, weight: str = "regular", max_width: int | None = None):
    draw = ImageDraw.Draw(base, "RGBA")
    if max_width:
        text = ellipsize(draw, text, size, weight, max_width)
    tw, th = measure_mixed(draw, text, size, weight)
    x, y = xy
    cursor = x
    for run, kind in split_runs(text):
        if kind == "emoji":
            img = emoji_image(run, int(size * 1.05))
            if img:
                base.alpha_composite(img, (int(cursor), int(y + (th - img.height) / 2)))
                cursor += img.width
            else:
                ft = text_font("latin", size, weight)
                draw.text((cursor, y), "□", font=ft, fill=fill)
                cursor += bbox(draw, "□", ft)[0]
        else:
            ft = text_font(kind, size, weight)
            draw.text((cursor, y), run, font=ft, fill=fill)
            cursor += bbox(draw, run, ft)[0]


def fit_plain_font(draw: ImageDraw.ImageDraw, font_name: str, text: str, start_size: int, max_w: int) -> ImageFont.FreeTypeFont:
    size = start_size
    while size > 18:
        ft = f(font_name, size)
        if bbox(draw, text, ft)[0] <= max_w:
            return ft
        size -= 1
    return f(font_name, size)


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=255)
    return mask


def shadowed_round_rect(base: Image.Image, rect: tuple[int, int, int, int], radius: int, fill, outline, shadow=(0, 0, 0, 130), blur: int = 18, offset=(0, 12)):
    x0, y0, x1, y1 = rect
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer, "RGBA")
    sd.rounded_rectangle((x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]), radius, fill=shadow)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    shape = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sh = ImageDraw.Draw(shape, "RGBA")
    sh.rounded_rectangle(rect, radius, fill=fill, outline=outline, width=1)
    base.alpha_composite(shape)


def overlay_round_rect(base: Image.Image, rect: tuple[int, int, int, int], radius: int, fill=None, outline=None, width: int = 1):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer, "RGBA")
    ld.rounded_rectangle(rect, radius, fill=fill, outline=outline, width=width)
    base.alpha_composite(layer)


def gradient_rect(base: Image.Image, rect: tuple[int, int, int, int], c1, c2, radius: int, alpha: int = 255):
    x0, y0, x1, y1 = rect
    ww, hh = x1 - x0, y1 - y0
    grad = Image.new("RGBA", (ww, hh), (0, 0, 0, 0))
    gp = grad.load()
    for x in range(ww):
        t = x / max(1, ww - 1)
        col = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
        for y in range(hh):
            gp[x, y] = (*col, alpha)
    mask = rounded_mask((ww, hh), radius).point(lambda p: int(p * alpha / 255))
    grad.putalpha(mask)
    base.alpha_composite(grad, (x0, y0))


def _background_gradient() -> Image.Image:
    if _np is not None:
        x = _np.arange(W, dtype=_np.float64)[None, :]
        y = _np.arange(H, dtype=_np.float64)[:, None]
        g1 = _np.clip(1 - _np.hypot((x - 280) / 780, (y - 110) / 540), 0, None)
        g2 = _np.clip(1 - _np.hypot((x - 1280) / 820, (y - 290) / 620), 0, None)
        g3 = _np.clip(1 - _np.hypot((x - 760) / 1050, (y - 880) / 520), 0, None)
        out = _np.empty((H, W, 4), dtype=_np.uint8)
        out[..., 0] = (5 + 22 * g1 + 15 * g2 + 8 * g3).astype(_np.uint8)
        out[..., 1] = (8 + 9 * g1 + 8 * g2 + 18 * g3).astype(_np.uint8)
        out[..., 2] = (22 + 36 * g1 + 27 * g2 + 22 * g3).astype(_np.uint8)
        out[..., 3] = 255
        return Image.fromarray(out, "RGBA")
    img = Image.new("RGBA", (W, H), (*PALETTE["bg0"], 255))
    px = img.load()
    for y in range(H):
        for x in range(W):
            g1 = max(0, 1 - math.hypot((x - 280) / 780, (y - 110) / 540))
            g2 = max(0, 1 - math.hypot((x - 1280) / 820, (y - 290) / 620))
            g3 = max(0, 1 - math.hypot((x - 760) / 1050, (y - 880) / 520))
            px[x, y] = (int(5 + 22 * g1 + 15 * g2 + 8 * g3), int(8 + 9 * g1 + 8 * g2 + 18 * g3), int(22 + 36 * g1 + 27 * g2 + 22 * g3), 255)
    return img


def background(seed: int) -> Image.Image:
    img = _background_gradient()
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(seed)
    for _ in range(220):
        x, y = rng.randrange(W), rng.randrange(H)
        col = rng.choice([(139, 92, 246), (34, 211, 238), (236, 72, 153)])
        d.ellipse((x, y, x + 2, y + 2), fill=(*col, rng.randrange(20, 90)))
    for x in range(0, W, 36):
        d.line((x, 0, x, H), fill=(255, 255, 255, 5), width=1)
    for y in range(0, H, 36):
        d.line((0, y, W, y), fill=(255, 255, 255, 5), width=1)
    return img


def icon_people(d: ImageDraw.ImageDraw, x: int, y: int, s: int, col):
    d.ellipse((x + s * 0.36, y + s * 0.08, x + s * 0.64, y + s * 0.36), fill=col)
    d.rounded_rectangle((x + s * 0.23, y + s * 0.42, x + s * 0.77, y + s * 0.83), int(s * 0.16), fill=col)
    d.ellipse((x + s * 0.12, y + s * 0.20, x + s * 0.34, y + s * 0.42), fill=col)
    d.ellipse((x + s * 0.66, y + s * 0.20, x + s * 0.88, y + s * 0.42), fill=col)
    d.rounded_rectangle((x + s * 0.05, y + s * 0.48, x + s * 0.36, y + s * 0.78), int(s * 0.12), fill=col)
    d.rounded_rectangle((x + s * 0.64, y + s * 0.48, x + s * 0.95, y + s * 0.78), int(s * 0.12), fill=col)


def icon_user(d: ImageDraw.ImageDraw, x: int, y: int, s: int, col):
    d.ellipse((x + s * 0.31, y + s * 0.08, x + s * 0.69, y + s * 0.46), fill=col)
    d.rounded_rectangle((x + s * 0.18, y + s * 0.53, x + s * 0.82, y + s * 0.90), int(s * 0.18), fill=col)


def icon_note(d: ImageDraw.ImageDraw, x: int, y: int, s: int, col):
    d.ellipse((x + s * 0.10, y + s * 0.62, x + s * 0.40, y + s * 0.92), fill=col)
    d.rectangle((x + s * 0.34, y + s * 0.13, x + s * 0.44, y + s * 0.72), fill=col)
    d.polygon([(x + s * 0.43, y + s * 0.13), (x + s * 0.86, y + s * 0.04), (x + s * 0.86, y + s * 0.23), (x + s * 0.43, y + s * 0.32)], fill=col)


def icon_clock(d: ImageDraw.ImageDraw, x: int, y: int, s: int, col):
    d.ellipse((x, y, x + s, y + s), outline=col, width=max(3, s // 13))
    d.line((x + s / 2, y + s / 2, x + s / 2, y + s * 0.25), fill=col, width=max(3, s // 17))
    d.line((x + s / 2, y + s / 2, x + s * 0.70, y + s * 0.62), fill=col, width=max(3, s // 17))


def draw_icon(d: ImageDraw.ImageDraw, kind: str, x: int, y: int, s: int, col):
    if kind == "group":
        icon_people(d, x, y, s, col)
    elif kind == "user":
        icon_user(d, x, y, s, col)
    elif kind == "clock":
        icon_clock(d, x, y, s, col)
    else:
        icon_note(d, x, y, s, col)


def draw_crown(d: ImageDraw.ImageDraw, x: int, y: int, s: int, col):
    d.polygon([(x, y + s * 0.76), (x + s * 0.15, y + s * 0.34), (x + s * 0.39, y + s * 0.58), (x + s * 0.50, y + s * 0.18), (x + s * 0.61, y + s * 0.58), (x + s * 0.85, y + s * 0.34), (x + s, y + s * 0.76)], fill=col)
    d.rounded_rectangle((x + s * 0.08, y + s * 0.72, x + s * 0.92, y + s * 0.88), 2, fill=col)


def draw_header(base: Image.Image, title: str, tagline: str, seed: int):
    d = ImageDraw.Draw(base, "RGBA")
    rng = random.Random(seed + 1)
    for cx, cy, rx, ry, col in [(575, 64, 158, 40, PALETTE["violet"]), (772, 68, 205, 48, PALETTE["cyan"]), (970, 77, 180, 44, PALETTE["pink"])]:
        for xx in range(-rx, rx, 10):
            for yy in range(-ry, ry, 10):
                if (xx / rx) ** 2 + (yy / ry) ** 2 < rng.uniform(0.55, 1.04):
                    d.rounded_rectangle((cx + xx, cy + yy, cx + xx + 4, cy + yy + 4), 1, fill=(*col, rng.randrange(40, 115)))
    for x, accent, kind in [(150, PALETTE["cyan"], "group"), (1386, PALETTE["pink"], "sound")]:
        shadowed_round_rect(base, (x - 78, 42, x + 78, 198), 42, (15, 22, 45, 115), (*accent, 70), blur=22, offset=(0, 8))
        d.rounded_rectangle((x - 78, 42, x + 78, 198), 42, outline=(*accent, 100), width=1)
        if kind == "group":
            draw_icon(d, "group", x - 42, 80, 84, (*accent, 190))
            d.arc((x - 55, 61, x + 55, 181), 25, 335, fill=(255, 255, 255, 55), width=2)
        else:
            d.arc((x - 52, 71, x + 52, 169), 190, 350, fill=(*accent, 190), width=5)
            d.rounded_rectangle((x - 58, 113, x - 32, 166), 11, outline=(34, 211, 238, 170), width=4)
            d.rounded_rectangle((x + 32, 113, x + 58, 166), 11, outline=(*accent, 170), width=4)
            d.line([(x - 36 + i, 139 + math.sin(i / 3.5) * 10 + math.sin(i / 1.4) * 3) for i in range(78)], fill=(236, 72, 153, 210), width=3)
    title_font = f("display_bold", 94)
    tw, _ = bbox(d, title, title_font)
    x = (W - tw) // 2
    d.text((x, 70), title, font=title_font, fill=(246, 248, 252, 255), stroke_width=1, stroke_fill=(9, 12, 23, 220))
    d.line((x + 4, 177, x + tw - 4, 177), fill=(255, 255, 255, 25), width=1)
    pill = (492, 202, 1044, 240) if len(tagline) > 18 else (515, 202, 1021, 240)
    gradient_rect(base, pill, (36, 42, 78), (53, 31, 76), 19, 205)
    d.rounded_rectangle(pill, 19, outline=(255, 255, 255, 32), width=1)
    tf = f("mono", 22)
    ttw, _ = bbox(d, tagline, tf)
    d.text(((W - ttw) // 2, 209), tagline, font=tf, fill=(202, 213, 255, 235))
    d.line((342, 221, 472, 221), fill=(*PALETTE["cyan"], 135), width=2)
    d.line((1064, 221, 1194, 221), fill=(*PALETTE["pink"], 135), width=2)


def draw_panel(base: Image.Image, x: int, y: int, panel_w: int, panel_h: int, title: str, kind: str, accent, data):
    d = ImageDraw.Draw(base, "RGBA")
    shadowed_round_rect(base, (x, y, x + panel_w, y + panel_h), 24, (*PALETTE["card"], 218), (*accent, 88), shadow=(*accent, 34), blur=18, offset=(0, 10))
    gradient_rect(base, (x, y, x + panel_w, y + 82), accent, (22, 28, 54), 24, 105)
    overlay_round_rect(base, (x, y, x + panel_w, y + panel_h), 24, outline=(255, 255, 255, 22), width=1)
    d.line((x + 24, y + 82, x + panel_w - 24, y + 82), fill=(*accent, 125), width=1)
    overlay_round_rect(base, (x + 24, y + 22, x + 78, y + 76), 18, fill=(255, 255, 255, 18), outline=(*accent, 120), width=1)
    draw_icon(d, kind, x + 39, y + 35, 26, (244, 247, 251, 235))
    d.text((x + 94, y + 25), title, font=f("display_bold", 32), fill=(248, 250, 252, 250))
    draw_crown(d, x + panel_w - 64, y + 34, 38, (*accent, 210))

    row_top = y + 96
    row_h = 63
    name_x = x + 92
    value_right = x + panel_w - 29
    text_max_w = panel_w - 222
    for idx, (name, value, unit) in enumerate(data, 1):
        yy = row_top + (idx - 1) * (row_h + 5)
        rank_col = [PALETTE["gold"], PALETTE["silver"], PALETTE["bronze"]][idx - 1] if idx <= 3 else accent
        overlay_round_rect(base, (x + 18, yy, x + panel_w - 18, yy + row_h), 16, fill=(255, 255, 255, 18 if idx == 1 else 10), outline=(255, 255, 255, 20), width=1)
        if idx <= 3:
            overlay_round_rect(base, (x + 18, yy, x + 24, yy + row_h), 3, fill=(*rank_col, 190))
        badge = (x + 36, yy + 11, x + 82, yy + 57)
        gradient_rect(base, badge, rank_col, accent, 13, 220 if idx <= 3 else 185)
        overlay_round_rect(base, badge, 13, outline=(255, 255, 255, 42), width=1)
        rf = f("display_bold", 28)
        rw, rh = bbox(d, str(idx), rf)
        d.text((x + 59 - rw / 2, yy + 24 - rh / 2), str(idx), font=rf, fill=(255, 255, 255, 255))
        draw_mixed(base, (name_x, yy + 20), name, 24, (*PALETTE["text"], 246), "bold", max_width=text_max_w)
        value_text = str(value)
        vf = fit_plain_font(d, "display_bold", value_text, 31, 96)
        d.text((value_right, yy + 11), value_text, font=vf, fill=(*accent, 255), anchor="ra")
        d.text((value_right, yy + 41), unit, font=f("sans_regular", 16), fill=(*PALETTE["muted"], 225), anchor="ra")


def draw_stats(base: Image.Image, stats_title: str, stats_subtitle: str, stats):
    d = ImageDraw.Draw(base, "RGBA")
    x, y = MARGIN, 728
    w = W - MARGIN * 2
    shadowed_round_rect(base, (x, y, x + w, y + 220), 26, (8, 13, 28, 224), (255, 255, 255, 38), shadow=(0, 0, 0, 150), blur=22, offset=(0, 12))
    d.text((W // 2, y + 18), stats_title, font=f("display_bold", 33), fill=(248, 250, 252, 245), anchor="ma")
    d.text((W // 2, y + 72), stats_subtitle, font=f("sans_regular", 16), fill=(*PALETTE["muted"], 205), anchor="ma")
    card_gap = 18
    card_w = (w - 60 - card_gap * 2) // 3
    card_y = y + 96
    for i, (kind, value, label, desc, accent) in enumerate(stats):
        cx = x + 30 + i * (card_w + card_gap)
        shadowed_round_rect(base, (cx, card_y, cx + card_w, card_y + 104), 22, (*PALETTE["card2"], 218), (*accent, 66), shadow=(*accent, 20), blur=12, offset=(0, 5))
        overlay_round_rect(base, (cx + 22, card_y + 24, cx + 78, card_y + 80), 18, fill=(*accent, 28), outline=(*accent, 120), width=1)
        draw_icon(d, kind, cx + 38, card_y + 39, 25, (*accent, 230))
        value_font = fit_plain_font(d, "display_bold", value, 42 if len(value) <= 6 else 35, card_w - 176)
        d.text((cx + 98, card_y + 20), value, font=value_font, fill=(*accent, 255))
        d.text((cx + 100, card_y + 65), label, font=f("sans_bold", 16), fill=(241, 245, 249, 232))
        d.text((cx + card_w - 24, card_y + 69), desc, font=f("sans_regular", 14), fill=(*PALETTE["muted"], 190), anchor="ra")


def draw_footer(base: Image.Image):
    d = ImageDraw.Draw(base, "RGBA")
    y = 956
    prefix = "Powered by "
    brand = "Telecast"
    pf = f("sans_regular", 20)
    bf = f("display_bold", 22)
    pw, _ = bbox(d, prefix, pf)
    bw, _ = bbox(d, brand, bf)
    total_w = pw + bw
    start_x = (W - total_w) // 2
    d.text((start_x, y), prefix, font=pf, fill=(200, 210, 230, 190))
    brand_x = start_x + pw
    glow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow_layer, "RGBA").text((brand_x, y), brand, font=bf, fill=(34, 211, 238, 120))
    base.alpha_composite(glow_layer.filter(ImageFilter.GaussianBlur(7)))

    brand_left, brand_top, brand_right, brand_bottom = d.textbbox((0, 0), brand, font=bf)
    pad = 10
    grad_w = brand_right - brand_left + pad * 2
    grad_h = brand_bottom - brand_top + pad * 2
    brand_grad = Image.new("RGBA", (grad_w, grad_h), (0, 0, 0, 0))
    gp = brand_grad.load()
    for gx in range(grad_w):
        t = gx / max(1, grad_w - 1)
        col = tuple(int((34, 211, 238)[i] * (1 - t) + (139, 92, 246)[i] * t) for i in range(3))
        for gy in range(grad_h):
            gp[gx, gy] = (*col, 255)
    mask_layer = Image.new("RGBA", (grad_w, grad_h), (0, 0, 0, 0))
    ImageDraw.Draw(mask_layer, "RGBA").text((pad - brand_left, pad - brand_top), brand, font=bf, fill=(255, 255, 255, 255))
    *_, alpha = mask_layer.split()
    brand_grad.putalpha(alpha)
    base.alpha_composite(brand_grad, (brand_x + brand_left - pad, y + brand_top - pad))
    d.line((MARGIN, y + 13, start_x - 28, y + 13), fill=(255, 255, 255, 22), width=1)
    d.line((start_x + total_w + 28, y + 13, W - MARGIN, y + 13), fill=(255, 255, 255, 22), width=1)


def vignette(base: Image.Image):
    if _np is not None:
        x = _np.arange(W, dtype=_np.float64)[None, :]
        y = _np.arange(H, dtype=_np.float64)[:, None]
        dx = _np.abs(x - W / 2) / (W / 2)
        dy = _np.abs(y - H / 2) / (H / 2)
        a = _np.clip(118 * _np.clip(dx * dx + dy * dy - 0.55, 0, None), None, 130).astype(_np.uint8)
        overlay = _np.zeros((H, W, 4), dtype=_np.uint8)
        overlay[..., 3] = a
        base.alpha_composite(Image.fromarray(overlay, "RGBA"))
        return
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    px = overlay.load()
    for y in range(H):
        for x in range(W):
            dx = abs(x - W / 2) / (W / 2)
            dy = abs(y - H / 2) / (H / 2)
            px[x, y] = (0, 0, 0, min(130, int(118 * max(0, dx * dx + dy * dy - 0.55))))
    base.alpha_composite(overlay)


def render_banner(output: Path, title: str, tagline: str, panels, stats_title: str, stats_subtitle: str, stats, seed: int):
    base = background(seed)
    draw_header(base, title, tagline, seed)
    count = len(panels)
    panel_w = (W - (MARGIN * 2) - GAP * (count - 1)) // count
    panel_y = 278 if count == 2 else 266
    panel_h = 438
    for i, (panel_title, kind, accent, data) in enumerate(panels):
        draw_panel(base, MARGIN + i * (panel_w + GAP), panel_y, panel_w, panel_h, panel_title, kind, accent, data)
    draw_stats(base, stats_title, stats_subtitle, stats)
    draw_footer(base)
    vignette(base)
    output.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(output, quality=96)
