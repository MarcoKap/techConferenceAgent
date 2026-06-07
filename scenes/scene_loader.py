"""Load scene definitions from optional JSON config.

If `SCENES_CONFIG_PATH` is not set, built-in defaults are used.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import config
from scenes.scene_definitions import (
    AudioConfig,
    DisplayConfig,
    LedConfig,
    PrintConfig,
    SCENES,
    SceneConfig,
    ServoConfig,
)


def _resolve_color(value: Any, fallback: tuple[int, int, int]) -> tuple[int, int, int]:
    if isinstance(value, str):
        named = getattr(config, f"COLOR_{value.strip().upper()}", None)
        if isinstance(named, tuple) and len(named) == 3:
            return named
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return (int(value[0]), int(value[1]), int(value[2]))
    return fallback


def _from_item(item: dict[str, Any], base: SceneConfig) -> SceneConfig:
    display_src = item.get("display", {})
    leds_src = item.get("leds", {})
    servo_src = item.get("servo", {})
    audio_src = item.get("audio", {})
    print_src = item.get("printing", {})

    return SceneConfig(
        id=str(item.get("id", base.id)),
        name=str(item.get("name", base.name)),
        display=DisplayConfig(
            eye_color=_resolve_color(display_src.get("eye_color"), base.display.eye_color),
            eye_shape=str(display_src.get("eye_shape", base.display.eye_shape)),
            pupil_animation=str(
                display_src.get("pupil_animation", base.display.pupil_animation)
            ),
            mouth_type=str(display_src.get("mouth_type", base.display.mouth_type)),
            visual_mode=str(display_src.get("visual_mode", base.display.visual_mode)),
            overlay_lines=tuple(
                str(line)
                for line in display_src.get("overlay_lines", list(base.display.overlay_lines))
            ),
        ),
        leds=LedConfig(
            animation_name=str(
                leds_src.get("animation_name", base.leds.animation_name)
            ),
            color_primary=_resolve_color(
                leds_src.get("color_primary"), base.leds.color_primary
            ),
            color_secondary=_resolve_color(
                leds_src.get("color_secondary"), base.leds.color_secondary
            ),
            speed=float(leds_src.get("speed", base.leds.speed)),
        ),
        servo=ServoConfig(
            angle_profile=str(
                servo_src.get("angle_profile", base.servo.angle_profile)
            ),
            speed=float(servo_src.get("speed", base.servo.speed)),
        ),
        audio=AudioConfig(
            filename=audio_src.get("filename", base.audio.filename),
            loop=bool(audio_src.get("loop", base.audio.loop)),
        ),
        printing=PrintConfig(
            pdf_path=print_src.get("pdf_path", base.printing.pdf_path),
            auto_print_on_enter=bool(
                print_src.get("auto_print_on_enter", base.printing.auto_print_on_enter)
            ),
        ),
    )


def load_scenes() -> list[SceneConfig]:
    path_raw = config.SCENES_CONFIG_PATH
    if not path_raw:
        return list(SCENES)

    path = Path(path_raw)
    if not path.exists():
        print(f"[scene] config not found, using defaults: {path}")
        return list(SCENES)

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = payload.get("scenes") if isinstance(payload, dict) else payload
        if not isinstance(entries, list) or not entries:
            print(f"[scene] invalid config format, using defaults: {path}")
            return list(SCENES)

        defaults = list(SCENES)
        loaded: list[SceneConfig] = []
        for i, item in enumerate(entries):
            if not isinstance(item, dict):
                continue
            base = defaults[min(i, len(defaults) - 1)]
            loaded.append(_from_item(item, base))

        if not loaded:
            print(f"[scene] no valid scene entries, using defaults: {path}")
            return list(SCENES)

        print(f"[scene] loaded {len(loaded)} scenes from {path}")
        return loaded
    except Exception as exc:
        print(f"[scene] failed to load config, using defaults: {exc}")
        return list(SCENES)
