#!/usr/bin/env python3
"""Render and print a conference welcome + weather ticket for thermal printers.

The script creates a grayscale image suitable for small thermal printers and can
optionally submit it through TiMini-Print CLI.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import io
import shlex
import subprocess
import tempfile
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


VIENNA_LAT = 48.2082
VIENNA_LON = 16.3738
DEFAULT_LOGO_URL = (
    "https://www.techconference.at/wp-content/themes/techconference.at/assets/svg/"
    "techconference_logo_full.svg"
)


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ]
    for path in candidates:
        p = Path(path)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def _draw_bold_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    font: ImageFont.ImageFont,
    fill: int = 0,
    strength: int = 2,
) -> None:
    x, y = xy
    draw.text((x, y), text, fill=fill, font=font)
    for dx in range(1, strength + 1):
        draw.text((x + dx, y), text, fill=fill, font=font)


def _wrap_text(text: str, max_chars: int = 30) -> list[str]:
    chunks: list[str] = []
    for line in text.split("\n"):
        wrapped = textwrap.wrap(line, width=max_chars, break_long_words=False)
        if not wrapped:
            chunks.append("")
        else:
            chunks.extend(wrapped)
    return chunks


def _logo_from_source(logo_path: Path | None, logo_url: str | None) -> Image.Image | None:
    raw_bytes = None
    source_name = ""
    if logo_path is not None and logo_path.exists():
        raw_bytes = logo_path.read_bytes()
        source_name = logo_path.name.lower()
    elif logo_url:
        req = urllib.request.Request(
            logo_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            raw_bytes = response.read()
        source_name = logo_url.lower()

    if raw_bytes is None:
        return None

    if source_name.endswith(".svg"):
        try:
            import cairosvg

            raw_bytes = cairosvg.svg2png(bytestring=raw_bytes)
        except Exception as exc:
            raise RuntimeError(
                "SVG logo conversion failed. Install cairosvg in this venv or use a PNG logo."
            ) from exc

    logo = Image.open(io.BytesIO(raw_bytes)).convert("RGBA")
    alpha = logo.getchannel("A")

    # Convert any visible logo shape (including white logos) to black pixels.
    black_logo = Image.new("L", logo.size, color=255)
    black_logo.paste(0, mask=alpha)
    return black_logo


def _to_iso_date(value: str) -> str:
    value = value.strip()
    if "." in value:
        parsed = dt.datetime.strptime(value, "%d.%m.%Y").date()
        return parsed.isoformat()
    parsed = dt.date.fromisoformat(value)
    return parsed.isoformat()


def _weather_code_label(code: int) -> str:
    labels = {
        0: "Klar",
        1: "Leicht bewolkt",
        2: "Bewolkt",
        3: "Bedeckt",
        45: "Neblig",
        48: "Raureifnebel",
        51: "Nieselregen",
        53: "Nieselregen",
        55: "Starker Nieselregen",
        61: "Regen",
        63: "Regen",
        65: "Starker Regen",
        71: "Schnee",
        73: "Schnee",
        75: "Starker Schnee",
        80: "Regenschauer",
        81: "Regenschauer",
        82: "Starke Schauer",
        95: "Gewitter",
        96: "Gewitter/Hagel",
        99: "Gewitter/Hagel",
    }
    return labels.get(code, f"Code {code}")


def _draw_weather_icon(draw: ImageDraw.ImageDraw, x: int, y: int, code: int) -> None:
    # Simple monochrome icon set for thermal output.
    if code == 0:
        draw.ellipse((x + 8, y + 8, x + 40, y + 40), outline=0, width=2)
        draw.line((x + 24, y + 0, x + 24, y + 10), fill=0, width=2)
        draw.line((x + 24, y + 38, x + 24, y + 48), fill=0, width=2)
        draw.line((x + 0, y + 24, x + 10, y + 24), fill=0, width=2)
        draw.line((x + 38, y + 24, x + 48, y + 24), fill=0, width=2)
        return

    if code in {1, 2, 3, 45, 48}:
        draw.ellipse((x + 6, y + 16, x + 22, y + 30), outline=0, width=2)
        draw.ellipse((x + 16, y + 10, x + 34, y + 30), outline=0, width=2)
        draw.ellipse((x + 28, y + 16, x + 44, y + 30), outline=0, width=2)
        draw.rectangle((x + 10, y + 24, x + 40, y + 34), outline=0, width=2)
        return

    if code in {61, 63, 65, 80, 81, 82, 51, 53, 55}:
        _draw_weather_icon(draw, x, y, 2)
        draw.line((x + 14, y + 38, x + 10, y + 46), fill=0, width=2)
        draw.line((x + 24, y + 38, x + 20, y + 46), fill=0, width=2)
        draw.line((x + 34, y + 38, x + 30, y + 46), fill=0, width=2)
        return

    if code in {95, 96, 99}:
        _draw_weather_icon(draw, x, y, 3)
        draw.polygon([(x + 24, y + 36), (x + 18, y + 48), (x + 26, y + 48), (x + 20, y + 58)], fill=0)
        return

    # Fallback for less common codes.
    draw.rectangle((x + 4, y + 4, x + 44, y + 44), outline=0, width=2)
    draw.text((x + 10, y + 16), "?", fill=0, font=ImageFont.load_default())


def _fetch_weather(date_iso: str) -> dict:
    query = urllib.parse.urlencode(
        {
            "latitude": VIENNA_LAT,
            "longitude": VIENNA_LON,
            "timezone": "Europe/Vienna",
            "daily": (
                "weathercode,temperature_2m_max,temperature_2m_min,"
                "precipitation_probability_max"
            ),
            "start_date": date_iso,
            "end_date": date_iso,
        }
    )
    url = f"https://api.open-meteo.com/v1/forecast?{query}"
    with urllib.request.urlopen(url, timeout=12) as response:
        payload = json.loads(response.read().decode("utf-8"))
    daily = payload.get("daily", {})
    return {
        "date": date_iso,
        "code": int(daily.get("weathercode", [0])[0]),
        "temp_max": float(daily.get("temperature_2m_max", [0.0])[0]),
        "temp_min": float(daily.get("temperature_2m_min", [0.0])[0]),
        "precip": float(daily.get("precipitation_probability_max", [0.0])[0]),
    }


def _render_ticket(
    out_path: Path,
    logo_path: Path | None,
    logo_url: str | None,
    title: str,
    greeting: str,
    weather: dict | None,
    width: int,
) -> None:
    title_font = _load_font(34)
    body_font = _load_font(24)
    small_font = _load_font(20)

    logo_h = 0
    logo_img = None
    logo_img = _logo_from_source(logo_path, logo_url)
    if logo_img is not None:
        ratio = min((width - 20) / logo_img.width, 1.0)
        logo_size = (max(1, int(logo_img.width * ratio)), max(1, int(logo_img.height * ratio)))
        logo_img = logo_img.resize(logo_size)
        logo_h = logo_size[1] + 14

    greeting_lines = _wrap_text(greeting, max_chars=26)
    text_h = 44 + (len(greeting_lines) * 28)
    weather_h = 150
    total_h = 14 + logo_h + text_h + weather_h + 20

    canvas = Image.new("L", (width, total_h), 255)
    draw = ImageDraw.Draw(canvas)
    y = 10

    if logo_img is not None:
        x = (width - logo_img.width) // 2
        canvas.paste(logo_img, (x, y))
        y += logo_h

    _draw_bold_text(draw, (10, y), title, font=title_font, strength=2)
    y += 40

    for line in greeting_lines:
        _draw_bold_text(draw, (10, y), line, font=body_font, strength=2)
        y += 26

    draw.line((8, y + 4, width - 8, y + 4), fill=0, width=2)
    y += 14

    _draw_bold_text(draw, (10, y), "Wetter Wien", font=body_font, strength=2)
    y += 30

    if weather is None:
        _draw_bold_text(draw, (10, y), "Nicht verfuegbar (offline/API)", font=small_font, strength=2)
    else:
        label = _weather_code_label(weather["code"])
        _draw_bold_text(draw, (10, y), f"Datum: {weather['date']}", font=small_font, strength=2)
        y += 24
        _draw_bold_text(draw, (10, y), f"{label}", font=small_font, strength=2)
        y += 24
        _draw_bold_text(
            draw,
            (10, y),
            f"Temp: {weather['temp_min']:.1f}..{weather['temp_max']:.1f} C",
            font=small_font,
            strength=2,
        )
        y += 24
        _draw_bold_text(draw, (10, y), f"Regenrisiko: {weather['precip']:.0f}%", font=small_font, strength=2)
        _draw_weather_icon(draw, width - 92, y - 70, weather["code"])

    draw.line((8, total_h - 12, width - 8, total_h - 12), fill=0, width=2)
    canvas.save(out_path)


def _print_with_timiniprint(
    image_path: Path,
    cmd: str,
    bluetooth: str | None,
    serial: str | None,
    darkness: int,
) -> None:
    parts = shlex.split(cmd)
    if not parts:
        raise RuntimeError("TiMini command is empty")

    args = [*parts]
    if serial:
        args.extend(["--serial", serial])
    elif bluetooth:
        args.extend(["--bluetooth", bluetooth])
    args.extend(["--darkness", str(max(1, min(5, darkness)))])
    args.append(str(image_path))

    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip()
        raise RuntimeError(message or "TiMini print failed")
    print((result.stdout or "Print queued").strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Create and optionally print conference ticket")
    parser.add_argument("--date", default="09.06.2026", help="Forecast date (DD.MM.YYYY or YYYY-MM-DD)")
    parser.add_argument("--logo", type=Path, default=None, help="Path to conference logo image")
    parser.add_argument("--logo-url", default=DEFAULT_LOGO_URL, help="Logo URL (SVG or image)")
    parser.add_argument("--title", default="techConference 2026", help="Ticket title")
    parser.add_argument(
        "--greeting",
        default="Willkommen zur techConference!\nWir wuenschen euch einen inspirierenden Tag.",
        help="Greeting text; use \\n for line breaks",
    )
    parser.add_argument("--width", type=int, default=384, help="Thermal print width in pixels")
    parser.add_argument("--output", type=Path, default=None, help="Output PNG path")
    parser.add_argument("--print", action="store_true", help="Print via TiMini-Print CLI")
    parser.add_argument(
        "--timiniprint-cmd",
        default=(
            "/Users/marco/Source/techConferenceAgent/TiMini-Print/.venv/bin/python "
            "/Users/marco/Source/techConferenceAgent/TiMini-Print/timiniprint_command_line.py"
        ),
        help="TiMini-Print command",
    )
    parser.add_argument("--bluetooth", default="X6h-0000", help="Printer bluetooth name/address")
    parser.add_argument("--serial", default=None, help="Serial device path (overrides bluetooth)")
    parser.add_argument("--darkness", type=int, default=5, help="TiMini print darkness 1-5")
    args = parser.parse_args()

    date_iso = _to_iso_date(args.date)

    weather = None
    try:
        weather = _fetch_weather(date_iso)
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, ValueError) as exc:
        print(f"[warn] weather unavailable: {exc}")

    greeting = args.greeting.replace("\\n", "\n")

    if args.output is None:
        out_path = Path(tempfile.gettempdir()) / f"conference_ticket_{date_iso}.png"
    else:
        out_path = args.output

    try:
        _render_ticket(
            out_path=out_path,
            logo_path=args.logo,
            logo_url=args.logo_url,
            title=args.title,
            greeting=greeting,
            weather=weather,
            width=args.width,
        )
    except Exception as exc:
        if args.logo is not None or args.logo_url:
            print(f"[warn] logo unavailable, rendering without logo: {exc}")
            _render_ticket(
                out_path=out_path,
                logo_path=None,
                logo_url=None,
                title=args.title,
                greeting=greeting,
                weather=weather,
                width=args.width,
            )
        else:
            raise
    print(f"Ticket image created: {out_path}")

    if args.print:
        _print_with_timiniprint(
            image_path=out_path,
            cmd=args.timiniprint_cmd,
            bluetooth=args.bluetooth,
            serial=args.serial,
            darkness=args.darkness,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
